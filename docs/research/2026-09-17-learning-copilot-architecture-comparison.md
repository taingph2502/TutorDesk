# So sánh kiến trúc DeepTutor, learning copilot và các vòng tự đánh giá đa tác tử

**Ngày khảo sát:** 2026-09-17

**Phạm vi:** kiến trúc điều phối, cơ chế cá nhân hoá, grounding/citation và các pattern tự đánh giá output.

**Mốc mã nguồn DeepTutor:** nhánh `main` tại commit [`897fce5`](https://github.com/HKUDS/DeepTutor/tree/897fce52f24bf22e6e50d8a3e4df532632a26322).

## Kết luận ngắn

Ba nhóm giải quyết ba bài toán khác nhau và nên được ghép theo lớp thay vì chọn một thay cho tất cả:

1. **DeepTutor** tối ưu cho một workspace học tập đa chức năng: một runtime/session context chung, một agent loop mặc định có thể gọi nhiều tool, các capability chuyên biệt, và memory file-backed có thể đọc/sửa/kiểm toán. Điểm khác biệt lớn nhất là **tính liên tục xuyên bề mặt** và **provenance của learner memory**, không phải một mô hình mastery toán học chặt như ALEKS.
2. **NotebookLM, Khanmigo, Anki/FSRS và ALEKS** là bốn kiểu cá nhân hoá khác nhau: theo tập nguồn, theo ngữ cảnh sư phạm và lịch sử học, theo lịch ôn trí nhớ, và theo trạng thái kiến thức trong một domain đóng. Chỉ NotebookLM công khai một cơ chế citation tới đúng đoạn nguồn rõ ràng ở cấp sản phẩm; “grounded in lesson/course” không đồng nghĩa với “mỗi claim có citation”.
3. **Board/debate room** là lớp kiểm định output. Debate tạo đa dạng giả thuyết; critique loop rẻ hơn nhưng dễ lặp lại cùng sai lầm; Constitutional-AI-style review cho rubric ổn định. Các paper cho thấy hiệu quả phụ thuộc mạnh vào task và tín hiệu kiểm chứng. Vì vậy, pattern phù hợp cho TutorDesk là **single orchestrator + reviewer có rubric + công cụ kiểm chứng bên ngoài**, chỉ fan-out thành debate khi rủi ro hoặc độ bất định đủ cao.

## 1. Khung so sánh

Trong báo cáo này:

- **Personalization** là trạng thái nào về người học được giữ, tín hiệu nào cập nhật nó, và trạng thái đó thay đổi nội dung/lộ trình ra sao.
- **Grounding** là việc generation được ràng buộc hoặc bổ sung bằng một corpus/domain model cụ thể.
- **Citation-grounding** mạnh hơn grounding: người dùng có thể truy từ claim/output về bằng chứng nguồn cụ thể.
- **Memory provenance** là truy vết một kết luận về người học về tương tác đã tạo ra kết luận đó. Nó khác **content citation**, vốn truy vết kiến thức trong câu trả lời về tài liệu học.

Các claim về sản phẩm đóng được giới hạn ở tài liệu chính thức công khai. Các đoạn ghi **Nhận định** là suy luận kiến trúc từ bằng chứng, không phải tuyên bố của nhà cung cấp.

## 2. DeepTutor

### 2.1. Runtime: một loop mặc định, nhiều tool và capability

Paper mô tả DeepTutor như một framework agent-native nơi mọi feature dùng chung “personalization substrate”; engine kết hợp static knowledge grounding với dynamic multi-resolution memory, đồng thời nối problem solving có citation với question generation điều chỉnh độ khó thành một tutoring loop khép kín ([paper, abstract](https://arxiv.org/abs/2604.26962)).

Mã nguồn hiện tại tách hai tầng plugin:

- **Tool** là thao tác đơn mà model chọn trong loop, ví dụ RAG, đọc nguồn, đọc/ghi memory, chạy code hoặc hỏi lại người dùng.
- **Capability** sở hữu cả turn và có pipeline/loop riêng, ví dụ chat, mastery, solve, question, research và visualize ([DeepTutor `AGENTS.md`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/AGENTS.md#L1-L70)). README hiện tại diễn đạt thận trọng hơn khẩu hiệu “one loop”: các mode dùng chung capability runtime và session context nhưng vẫn giữ các loop/pipeline chuyên biệt ([README](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/README.md#L225-L236)).

Loop chat mặc định là một hội thoại tăng dần trong một turn:

```text
user turn
   -> LLM round
      -> có tool call: append assistant + tool result vào cùng conversation -> round tiếp
      -> không có tool call: coi text là final answer -> kết thúc
   -> nếu hết exploration budget: settlement hữu hạn -> forced finish
```

Đây là contract được ghi ngay trong [`agent_loop.py`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/agents/loop/agent_loop.py#L1-L19); code cũng đặt giới hạn settlement để tránh tool loop chạy vô hạn ([cùng file](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/agents/loop/agent_loop.py#L80-L96)).

**Nhận định.** “Single agent loop nhiều capability” nên hiểu là **một đường điều phối và context chung, với chat/mastery dựa trên loop tool-use thống nhất**, không phải cam kết rằng mọi capability đều là cùng một hàm loop, cũng không có nghĩa hệ thống không bao giờ dùng subagent. Cách chia này giữ đường phổ biến đơn giản, trong khi các task như research/visualization vẫn có pipeline có cấu trúc.

### 2.2. Personalization substrate: memory file-backed ba lớp

Layout thực tế được khai báo trực tiếp trong [`paths.py`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/services/memory/paths.py#L1-L12):

| Lớp | Dạng lưu | Vai trò |
|---|---|---|
| **L1** | workspace snapshot + `trace/<surface>/<YYYY-MM-DD>.jsonl` | live/raw entity mirror và event trace append-only theo ngày, surface |
| **L2** | `L2/<surface>.md` | fact/summary đã curate cho từng surface |
| **L3** | `L3/<recent|profile|scope|preferences>.md` | tổng hợp xuyên surface theo slot |

Các surface hiện được type hoá là `chat`, `notebook`, `quiz`, `kb`, `book`, `partner`, `cowriter`; các slot L3 là `recent`, `profile`, `scope`, `preferences` ([`paths.py`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/services/memory/paths.py#L48-L60)). L1 có hai phần: event trace được append theo best-effort và có resolver tìm event theo id ([`trace.py`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/services/memory/trace.py#L1-L20), [`append`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/services/memory/trace.py#L66-L86)); snapshot adapter còn mirror live entity và lưu diff/fingerprint của workspace ([`snapshot/__init__.py`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/services/memory/snapshot/__init__.py#L1-L17), [`snapshot/store.py`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/services/memory/snapshot/store.py#L1-L36)). Updater L2 hiện đọc các entity mới từ snapshot, chia chunk, gọi LLM để extract fact, validate reference rồi atomic flush; sau đó có thể dedup/merge ([`update.py`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/services/memory/consolidator/modes/update.py#L140-L204)). Vì vậy, nói “L2 được tạo trực tiếp chỉ từ file trace JSONL” sẽ không chính xác với commit này.

Hai chi tiết triển khai cần phân biệt với mô tả marketing:

- **L2 → L1 là provenance cụ thể.** Fact L2 giữ reference đến raw entity; Memory Graph dựng cạnh mạnh tới đúng entity.
- **L3 → L2 hiện là provenance ở cấp surface, không phải luôn là exact L2 fact.** Prompt L3 yêu cầu `refs` là tên surface, cấm `m_xxx`/entry id ([`update_l3.yaml`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/services/memory/consolidator/prompts/en/update_l3.yaml#L1-L37)); updater giải thích L3 trỏ đến file L2/surface để tạo chuỗi `L3 -> L2 md -> L1` gọn hơn ([`update.py`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/services/memory/consolidator/modes/update.py#L466-L477)). Slot `preferences` tồn tại nhưng không được auto-consolidate ([`update.py`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/services/memory/consolidator/modes/update.py#L363-L375)).

### 2.3. Memory Graph là provenance graph, không phải learner concept graph

README mô tả ba vòng đồng tâm: L3 ở giữa, L2 ở vòng giữa, L1 ở ngoài; cạnh L2 → L1 là exact evidence, còn L3 → L2 là contributing-surface link ([README, Memory](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/README.md#L777-L792)). Code frontend khớp với mô tả này: L2 → L1 dùng cạnh `strong`, còn citation surface của L3 đi tới anchor ẩn của cluster L2 bằng cạnh `soft`; code để ngỏ một định dạng future cho exact L2 entry ([`memory-graph.ts`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/web/lib/memory-graph.ts#L569-L650)).

**Nhận định.** Memory Graph trả lời câu hỏi “kết luận hồ sơ này đến từ đâu?”, còn knowledge graph/mastery graph trả lời “khái niệm nào phụ thuộc khái niệm nào và learner đang biết gì?”. Không nên dùng Memory Graph như bằng chứng rằng DeepTutor đã có knowledge tracing kiểu ALEKS. Một giới hạn UI hiện tại cũng đáng chú ý: type backend có bốn slot L3, nhưng data layer của graph chỉ liệt kê `profile`, `recent`, `scope`, chưa đưa `preferences` vào vòng L3 ([`memory-graph.ts`](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/web/lib/memory-graph.ts#L20-L29)).

### 2.4. Hai kiến trúc “ba tầng” không phải một

Paper mô tả Dynamic Personal Memory bằng một **Trace Forest** có chiều abstraction từ coarse đến fine:

- Level 1 giữ session input và global summary;
- Level 2 giữ intermediate planning units;
- Level 3 giữ execution record/tool output/evidence/validation chi tiết;
- node có embedding và được truy xuất qua `SearchTrace`, `ListTraces`, `ReadNodes`; các memory agent tóm tắt session history, weakness và pedagogical reflection ([paper §2.1.2](https://arxiv.org/html/2604.26962#S2.SS1.SSS2)).

Ngược lại, product implementation file-backed tại commit khảo sát đi từ **L1 raw/live evidence → L2 per-surface curation → L3 cross-surface synthesis**, tức chiều abstraction tăng dần. Trong subtree `deeptutor/services/memory` công khai ở commit này, bằng chứng rõ nhất là file/snapshot/consolidator và graph viewer; chưa đủ bằng chứng để khẳng định Trace Forest có semantic embedding search trong paper chính là cùng một physical store với L1/L2/L3 Markdown/JSONL.

**Kết luận:** nên gọi Trace Forest là **research architecture trong paper**, còn L1/L2/L3 là **inspectable product implementation hiện hành**. Chúng cùng theo ý tưởng multi-resolution, evidence-backed personalization, nhưng mapping vật lý giữa hai bên chưa được công bố rõ. Đặc biệt, số “Level 1/2/3” của paper và “L1/L2/L3” của product không thể thay thế lẫn nhau.

### 2.5. Grounding và auditability

Knowledge bases ground nhiều workflow qua các engine RAG khác nhau; Reading có verified clickable citations, còn Research tạo cited reports ([README](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/README.md#L647-L657), [Knowledge Center](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/README.md#L741-L748)). Đây là **content grounding**. Chuỗi L1/L2/L3 lại là **learner-memory provenance**. Hai chuỗi có thể cùng xuất hiện trong một câu trả lời nhưng bảo đảm khác nhau; báo cáo công khai chưa chứng minh rằng mọi claim của mọi capability đều buộc phải có source citation.

**Điểm mạnh:** state có thể đọc/sửa, lưu local, audit được; surface mới có thể tham gia cùng substrate; raw trace không bị nén mất ngay.

**Rủi ro:** consolidation bằng LLM có thể rút ra fact sai; L3 chỉ trỏ surface khiến truy vết cuối cùng cần thêm bước tìm kiếm; PII/retention tăng theo raw trace; profile tự do không thay thế được mastery state có schema.

## 3. Các learning copilot khác

### 3.1. NotebookLM: source-scoped personalization, citation mạnh

NotebookLM cho phép chọn/bỏ nguồn dùng trong chat; câu trả lời dùng quote/text/image từ nguồn làm citation, hover để xem trích đoạn và click để nhảy đến vị trí tương ứng ([Google Help — Use chat](https://support.google.com/notebooklm/answer/16179559?hl=en)). Google cũng mô tả source-grounding như cách tạo một AI “versed in” tài liệu người dùng chọn, đồng thời cảnh báo vẫn phải fact-check và cung cấp citation về đoạn nguồn liên quan ([giới thiệu NotebookLM](https://blog.google/innovation-and-ai/technology/ai/notebooklm-google-ai/)). Flashcard/quiz cho chỉnh difficulty, audience/style/focus, ghi `Got it`/`Missed it` và ôn lại thẻ sai ([Google Help — Flashcards or Quizzes](https://support.google.com/gemininotebook/answer/16958963?hl=en-GB)).

**Nhận định.** Personalization công khai chủ yếu là theo **notebook/source set, prompt, output style và artifact progress**. Chưa có tài liệu công khai mô tả knowledge tracing bền vững xuyên notebook hay một learner model sâu. Citation chứng minh output bám passage nào, không chứng minh passage do người dùng tải lên là đúng hoặc đầy đủ.

### 3.2. Khanmigo: contextual pedagogical coach, user state nhẹ

Khanmigo được đặt cạnh bài học hiện tại, biết content learner đang làm và dùng prompt/hint/câu hỏi để giữ phần suy nghĩ cho learner thay vì chỉ đưa đáp án ([Khan Academy — Working through content](https://www.khanacademy.org/khan-for-educators/k4e-us-demo/xb78db74671c953a7%3Aget-to-know-khan-academy/xb78db74671c953a7%3Aexplore-the-student-experience/v/working-through-content)). “User Insights” công khai gồm conversation summaries, insight rút từ chat và Interests; preference còn có reading style/language ([deletion/retention practices](https://support.khanacademy.org/hc/en-us/articles/29415446635021-What-are-Khan-Academy-s-Deletion-Practices), [language/settings](https://support.khanacademy.org/hc/en-us/articles/19846024600845-How-can-I-change-the-default-language-that-Khanmigo-responds-in)).

Đáng chú ý, thử nghiệm sản phẩm 2025–2026 cho Khanmigo thêm structured learning history — recent attempts, demonstrated skill levels và prerequisite progress — và báo cáo summary lịch sử gần đây cải thiện next-item correctness 3,4% trên 608.000 tutoring threads; hai thay đổi history được báo cáo tổng cộng 6,1% ([Khan Academy, mô tả thử nghiệm](https://blog.khanacademy.org/how-khan-academy-is-building-a-better-ai-tutor-our-most-recent-learnings/)). Đây là first-party experiment, chưa nên suy rộng thành hiệu quả học dài hạn.

**Nhận định.** Khanmigo là **contextual coach có longitudinal state nhẹ và tín hiệu mastery từ nền tảng**, mạnh hơn NotebookLM ở scaffolding và hành vi học. Tuy nhiên “grounded in lesson” không phải per-claim citation. Tài liệu Khan Academy tự nhấn mạnh LLM không phải factual database và người học cần kiểm chứng nguồn ([cách LLM powering Khanmigo hoạt động](https://support.khanacademy.org/hc/en-us/articles/13888935335309-How-do-the-Large-Language-Models-powering-Khanmigo-work)). Không có public evidence đủ để khẳng định mọi câu trả lời có citation bắt buộc hoặc để mô tả retrieval pipeline nội bộ.

### 3.3. Anki/FSRS: cá nhân hoá thời điểm ôn, không cá nhân hoá nội dung giải thích

FSRS fit parameter từ review history cá nhân; scheduler dùng trạng thái difficulty, stability, retrievability và desired retention để cân bằng xác suất nhớ với workload. Parameter có thể tách theo preset/deck và optimizer học từ lịch sử review ([Anki Manual — FSRS](https://docs.ankiweb.net/deck-options)). Mô hình FSRS định nghĩa rõ ba đại lượng và forgetting curve ([FSRS algorithm](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm)).

**Nhận định.** Đây là personalization **hẹp nhưng định lượng tốt**: tối ưu *khi nào* hỏi lại card đã có, không tự suy luận *dạy thế nào* hoặc *nguồn nào đúng*. Anki hỗ trợ custom field, nên người soạn có thể thêm `book`, `page`, `source`, nhưng đó là convention authoring chứ không phải citation-verification pipeline ([Anki Manual — Fields](https://docs.ankiweb.net/editing)). Rating là tín hiệu nhiễu: chính manual cảnh báo dùng `Hard` thay `Again` khi đã quên sẽ làm interval sai. Không nên suy rộng memory state của card thành mastery của cả concept/domain.

### 3.4. ALEKS: learner state trong knowledge space đóng

ALEKS dựa trên Knowledge Space Theory: domain được biểu diễn bằng các knowledge state khả thi; adaptive assessment chọn câu dựa trên các câu trả lời trước để xác định learner đang mastery gì và “ready to learn” gì. Tài liệu lý thuyết chính thức nói khoảng 25–30 câu có thể định vị state trong cấu trúc có hàng triệu trạng thái khả thi ([ALEKS — Knowledge Space Theory](https://www.aleks.com/about_aleks/knowledge_space_theory)). Product duy trì map kiến thức, đề xuất learner làm việc ở biên của state hiện tại và dùng Knowledge Checks để xác nhận retention/cập nhật path ([About ALEKS](https://www.aleks.com/about_aleks), [How ALEKS works](https://www.aleks.com/about_aleks/HowALEKSWorks_TextDescription)).

**Nhận định.** ALEKS mạnh nhất ở **sequencing/prerequisite/mastery trong domain có cấu trúc**. Grounding nằm trong curriculum model và item bank đóng, không phải citation tới tài liệu gốc trong prose. Core engine là proprietary và nhiều con số hiệu quả trên trang public là vendor claim; không có public evidence cho inline citation ở cấp claim.

### 3.5. Ma trận cá nhân hoá và citation

| Hệ | Đơn vị state chính | Tín hiệu cập nhật | Output bị cá nhân hoá ở đâu | Citation/provenance công khai |
|---|---|---|---|---|
| **DeepTutor** | trace → surface facts → cross-surface profile | tương tác trên nhiều surface + consolidation | context, style/profile, tool/capability | content citations tuỳ workflow; memory provenance L2 → exact L1, L3 → surface |
| **NotebookLM** | notebook/source set + artifact progress | chọn nguồn, prompt/style, quiz/flashcard result | corpus và dạng output | inline citation tới passage/image nguồn rất rõ |
| **Khanmigo** | lesson context + summaries/interests + learning history | chat, activity, attempts, skill/prerequisite signals | scaffolding, hint, reading style, next response | lesson-grounded; chưa thấy cơ chế citation bắt buộc cho mọi claim |
| **Anki/FSRS** | per-card memory state + preset parameter | review history và rating | thời điểm/lịch ôn | provenance do tác giả card tự ghi; không có RAG citation built-in |
| **ALEKS** | knowledge state trong domain model | adaptive answers + periodic checks | next-ready topic/path | grounded vào curriculum/item bank đóng; chưa thấy inline source citation |

## 4. Multi-agent board/debate room để tự đánh giá output

### 4.1. Multi-agent debate

Pattern gốc cho nhiều model instance tạo answer riêng, đọc và critique answer của nhau qua nhiều vòng, rồi hội tụ về một answer chung. Paper của Du và cộng sự báo cáo cải thiện trên một số task reasoning/factuality; đồng thời chính paper nói convergence không được bảo đảm về lý thuyết và có ví dụ hội tụ về đáp án sai ([paper](https://arxiv.org/abs/2305.14325), đặc biệt §2.1–2.2 và appendix). Thí nghiệm dùng `gpt-3.5-turbo-0301`, nên không thể coi kết quả là định luật chung cho model/task hiện tại.

Một “board” triển khai thực dụng thường có:

```text
evidence packet
   -> N proposer/analyst độc lập
   -> cross-critique có claim/evidence id
   -> judge hoặc rule-based aggregator
   -> verified final + dissent/uncertainty
```

Ưu điểm là đa dạng hypothesis và phát hiện lỗi chéo. Nhược điểm là chi phí/latency tăng gần theo số agent × số vòng, shared blind spot vẫn tồn tại, và consensus có thể chỉ là conformity. Nghiên cứu ICLR 2024 về intrinsic self-correction còn cho thấy multi-agent debate không vượt self-consistency khi so cùng số sample trong các setup reasoning mà họ xét ([OpenReview paper](https://openreview.net/pdf?id=IkmD3fKBPQ)).

### 4.2. Critique–revise loop

Self-Refine dùng cùng một LLM làm generator, feedback provider và refiner, lặp đến tiêu chí dừng; không cần training bổ sung ([Self-Refine](https://arxiv.org/abs/2303.17651)). Kết quả paper tốt ở nhiều task preference/constrained generation, nhưng tăng rất ít ở math reasoning; tác giả quy nguyên nhân cho việc model khó nhận ra lỗi và cho thấy oracle feedback giúp hơn ([kết quả và phân tích](https://arxiv.org/abs/2303.17651#S3.SS3)). CRITIC bổ sung search/code/tool feedback trước khi sửa và nhấn mạnh vai trò của external feedback ([CRITIC](https://arxiv.org/abs/2305.11738)).

**Nhận định.** Critique loop phù hợp làm default reviewer vì rẻ và dễ quan sát hơn debate, nhưng critic không nên chỉ nhận lại cùng prompt/output. Cần cung cấp rubric, nguồn/citation map, test/checker hoặc một model khác; nếu không generator và critic có error correlation cao.

### 4.3. Constitutional-AI-style review

Constitutional AI dùng tập nguyên tắc làm chuẩn đánh giá. Bản gốc của Anthropic có hai phase training: supervised phase sinh self-critique/revision rồi fine-tune trên bản sửa; RL phase dùng AI preference để train preference model và RLAIF ([Anthropic paper summary](https://www.anthropic.com/news/constitutional-ai-harmlessness-from-ai-feedback)).

**Nhận định quan trọng.** Một inference-time “constitutional reviewer” trong ứng dụng chỉ **mượn pattern** principle → critique → revise; nó không tương đương hệ thống đã được Constitutional AI training. Giá trị của pattern là rubric được version hoá, inspect được và áp nhất quán cho pedagogy, safety, citation coverage và privacy.

### 4.4. So sánh ba pattern review

| Pattern | Topology | Cần external evidence? | Điểm mạnh | Failure mode chính | Nên dùng khi |
|---|---|---|---|---|---|
| **Debate/board** | nhiều proposer + cross-critique + judge | rất nên có | đa dạng hypothesis, bắt lỗi chéo | consensus sai, sycophancy, tốn token | task high-stakes/ambiguous, nhiều cách giải |
| **Critique–revise** | generator → critic → reviser | nên có checker/tool | đơn giản, rẻ, bounded | cùng model lặp blind spot | default QA, polishing, citation check |
| **Constitutional-style** | output → principle-based review → revise | rubric là bắt buộc; evidence tuỳ rule | nhất quán, audit policy dễ | constitution thiếu/xung đột, judge bias | safety, pedagogy policy, privacy, format |

## 5. Hàm ý kiến trúc cho TutorDesk

Đây là **đề xuất suy luận** từ so sánh, không phải claim từ các nguồn trên:

1. **Giữ single orchestrator cho đường phổ biến.** Một turn nên có một owner, một conversation state và budget/termination rõ như DeepTutor. Capability là policy/pipeline của turn, không cần biến mỗi feature thành một agent độc lập.
2. **Tách ba loại state.**

   - `learner_profile`: preference, mục tiêu, constraint; file-backed, user-editable, có provenance kiểu L1/L2/L3.
   - `mastery_state`: concept, prerequisite, evidence, confidence; schema chặt kiểu ALEKS.
   - `memory_schedule`: difficulty/stability/retrievability và due time kiểu FSRS.

   Trộn cả ba vào prose profile sẽ khó kiểm thử và dễ hallucinate mastery.
3. **Tách hai chuỗi provenance.** `answer claim -> content source passage` và `learner-model claim -> interaction/assessment event` phải có id/edge riêng. Memory Graph của DeepTutor là mẫu tốt cho chuỗi thứ hai; NotebookLM là mẫu tốt cho chuỗi thứ nhất.
4. **Review theo rủi ro.** Mặc định dùng một critique–revise pass có rubric. Chỉ mở debate board khi confidence thấp, citation conflict, nhiều lời giải cạnh tranh hoặc hành động có hậu quả cao.
5. **Board không được tự tạo “sự thật” từ consensus.** Mọi critic nên nhìn cùng một immutable evidence packet; factual/citation critic phải dùng retrieval/checker, pedagogy critic dùng learner/mastery state, judge phải giữ dissent và uncertainty nếu chưa phân giải.
6. **Version và audit reviewer.** Lưu rubric/constitution version, input evidence ids, critique, quyết định accept/revise, cost và stop reason. Không đẩy critique thô vào long-term learner profile trước khi fact đã qua validation.

Một pipeline tham chiếu tối thiểu:

```text
request
  -> orchestrator chọn capability + load scoped state
  -> retrieve evidence (content + learner-state provenance)
  -> generator/tool loop
  -> deterministic checks (schema, tests, citation coverage)
  -> rubric critic
       -> pass: answer
       -> revise once: answer
       -> high-risk unresolved: 2–3 independent reviewers + judge
  -> persist raw event; async curate profile/mastery/schedule separately
```

## 6. Giới hạn bằng chứng

- DeepTutor paper và repository thay đổi nhanh; report này pin code ở commit nêu đầu trang. Một số mô tả trong paper/README là product-level, còn chi tiết L3 surface-level citation và graph UI được lấy từ code tại commit đó.
- NotebookLM, Khanmigo và ALEKS là hệ đóng; tài liệu public không cho phép kết luận về schema, retrieval pipeline hoặc coverage nội bộ ngoài những gì hãng công bố.
- Các con số effectiveness của vendor được ghi như first-party evidence. Chúng không được dùng để xếp hạng hiệu quả học tổng quát.
- Các paper debate/self-refinement đánh giá tập model/task cụ thể. Kết quả cho thấy pattern khả thi, không bảo đảm cải thiện mọi output.
- Citation là provenance, không phải chứng minh truth. Nguồn sai, retrieval thiếu hoặc citation gắn sai vẫn có thể tạo câu trả lời sai.

## Nguồn chính

- DeepTutor: [paper](https://arxiv.org/abs/2604.26962), [repository tại commit khảo sát](https://github.com/HKUDS/DeepTutor/tree/897fce52f24bf22e6e50d8a3e4df532632a26322), [agent loop](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/agents/loop/agent_loop.py), [memory subsystem](https://github.com/HKUDS/DeepTutor/tree/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/services/memory).
- NotebookLM: [official chat/citation help](https://support.google.com/notebooklm/answer/16179559?hl=en), [Google product explanation](https://blog.google/innovation-and-ai/technology/ai/notebooklm-google-ai/).
- Khanmigo: [official product evidence update](https://blog.khanacademy.org/how-khan-academy-is-building-a-better-ai-tutor-our-most-recent-learnings/), [official lesson-context demonstration](https://www.khanacademy.org/khan-for-educators/k4e-us-demo/xb78db74671c953a7%3Aget-to-know-khan-academy/xb78db74671c953a7%3Aexplore-the-student-experience/v/working-through-content).
- Anki/FSRS: [Anki Manual](https://docs.ankiweb.net/deck-options), [FSRS algorithm](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm).
- ALEKS: [Knowledge Space Theory](https://www.aleks.com/about_aleks/knowledge_space_theory), [About ALEKS](https://www.aleks.com/about_aleks).
- Review patterns: [multi-agent debate](https://arxiv.org/abs/2305.14325), [Self-Refine](https://arxiv.org/abs/2303.17651), [CRITIC](https://arxiv.org/abs/2305.11738), [Constitutional AI](https://www.anthropic.com/news/constitutional-ai-harmlessness-from-ai-feedback), [limits of intrinsic self-correction](https://openreview.net/pdf?id=IkmD3fKBPQ).
