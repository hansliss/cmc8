# Instruction OCR search leads

Generated from all 226 PDF pages. These snippets are unreviewed OCR, including comparison architectures and possible false matches. They are navigation aids, not evidence. Use the curated references in [the instruction reference](instruction-set.md) for verified observations.

## LRM

Patterns: `LRM, LARM`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | LARM 0 1000RRR / ADR/ 3 LOAD FROM PROGRAM MEMORY. LRS 010 10RRR /ADR/ 3 LOAD FROM STORAGE MEMORY. |
| [125 / PDF 132](../bookpages/Page_131.jpg) | o Skriv in talet i minnet (SRM eller SRS) o Läs ut talet från minnet (LRM eller LRS) o Hoppa tillbaka (JMP) |
| [126 / PDF 133](../bookpages/Page_132.jpg) | 3 /ADR/ adress 3 /ADR/ adress 4 LRM 103 4 LRS 123 5 /ADR/ adress 5 SADR/ adress |
| [126 / PDF 133](../bookpages/Page_132.jpg) | gramminnet som är inställd på position 3. Om samma adress åter- finns på position 5 kommer det inskrivna ordet att utläsas av LRM- instruktionen. Om vi kör klockan långsamt ser vi ordet passera data- |
| [126 / PDF 133](../bookpages/Page_132.jpg) | instruktionen. Om vi kör klockan långsamt ser vi ordet passera data- bussen under deltiderna F2T2 - F2T5 under exekveringen av LRM- instruktionen. Detta verifierar att vi kan utläsa ett i minnet tidigare |
| [145 / PDF 152](../bookpages/Page_151.jpg) | $g0 LRM, 3 103 gl /Ljustyp 8/ 666 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | ETIKETT ADRESS MEMO-KOD KOMMENTAR <MASKINKOD 660 LRM, 3 193 281 /Ljustyp $/ ; 266 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | g11 /HIT/ pg4 FRAM g12 LRM, 3 103 013 /Ljustyp 1/ Ö67 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | g41 /Vänta 10/ 1gg g42 LRM, 3 163 43 /Ljustyp 4/ ; Ö72 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | $51 /Vänta 10/ 166 (52 LRM, 3 183 053 /Ljustyp 2/ : gp |
| [147 / PDF 154](../bookpages/Page_153.jpg) | ETIKETT ADRESS MEMO-KOD KOMMENTAR <MASKINKOD 060 LRM, 3 193 g61 /Ljustyp $/ 266 |

## LRS

Patterns: `LRS`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [front/back / PDF 5](../bookpages/Page_004.jpg) | 2.2 Mikroprogram i PLA 46 3 LRS-instruktionen 48 3 1 Tidsdiagram 48 |
| [front/back / PDF 5](../bookpages/Page_004.jpg) | 3 .2 Tidsuppdelat mikroprogram 51 3 .3 Mikroprogram för LRS-instruktionen 53 3 4 Skillnaden mellan LRS och SRS 54 |
| [front/back / PDF 5](../bookpages/Page_004.jpg) | 3 .3 Mikroprogram för LRS-instruktionen 53 3 4 Skillnaden mellan LRS och SRS 54 4 Tillståndsdiagram 55 |
| [30 / PDF 37](../bookpages/Page_036.jpg) | när Ladda ackumulatorn kallas för LRS (= load register from storage) det gäller CMC8. Motsvarande instruktion heter LDA (load accumulator) |
| [30 / PDF 37](../bookpages/Page_036.jpg) | Vi ska alltså göra ett mikroprogram för instruktionen LRS och vi ska I |
| [30 / PDF 37](../bookpages/Page_036.jpg) | Fig 32 Innebörden av instruktionen LRS |
| [31 / PDF 38](../bookpages/Page_037.jpg) | 7 g LRS adress |
| [31 / PDF 38](../bookpages/Page_037.jpg) | 110 = LRS |
| [31 / PDF 38](../bookpages/Page_037.jpg) | latorn. Observera att LRS tog 3 faser eller 3 cykler i anspråk. Det finns in- struktioner (exempelvis REL, nollställ linkvippan) som exekveras di- |
| [32 / PDF 39](../bookpages/Page_038.jpg) | Fig 3 Detre faserna hos LRS-instruktionen |
| [32 / PDF 39](../bookpages/Page_038.jpg) | I fig 3.3 visas de tre faserna i LRS-instruktionen. |
| [35 / PDF 42](../bookpages/Page_041.jpg) | vänt ett av dessa register som ackumulator och nu förstår vi bättre anledningen till MEMO-symbolen LRS, dvs ladda register (istället för ackumulator). |
| [37 / PDF 44](../bookpages/Page_043.jpg) | hur styrenheten arbetar tidsuppdelat. Vi ska åter studera den enkla instruktionen LRS men denna gång ta med tidsdiagrammet. Slutligen ska vi studera ett tillståndsdiagram (eller flödesplan) som visar hur |
| [40 / PDF 47](../bookpages/Page_046.jpg) | del. Den instruktion, LRS, som vi tidigare behandlat, har formatet |
| [43 / PDF 50](../bookpages/Page_049.jpg) | enordsinstruktion som förutsätter att en adress finns i X-registret (indexed addressing). LSX borde därmed vara snabbare än LRS som är en tvåordsinstruktion. I CMC8 tar emellertid båda dessa instruktioner |
| [44 / PDF 51](../bookpages/Page_050.jpg) | generationens" mikroprocessor, Zilog Z80. Vi känner här igen våra tre faser från LRS-instruktionen. I fig 4.5 betecknas de M1, M2 och M3 där M betyder "machine cycle". Instruktionen tar tydligen tre |
| [45 / PDF 52](../bookpages/Page_051.jpg) | cykler) för att hantera busstrafiken på ett rationellt sätt. CMC8 behö- ver 8 deltider i varje fas. Det betyder alltså att LRS-instruktionen be- höver 8x3 = 24 deltider för hämtning och exekvering av en instruktion. |
| [46 / PDF 53](../bookpages/Page_052.jpg) | instruktion behöver en viss uppsättning MOP:ar och i fig 4.7 har vi ritat ut hur MOP:arna ) (&) (0) osv styrs via OR-grindar från LRS- instruktionens AND-grind. |
| [48 / PDF 55](../bookpages/Page_054.jpg) | 3. LRS-instruktionen Vi är nu mogna att i detalj följa LRS-instruktionen (ladda register från |
| [48 / PDF 55](../bookpages/Page_054.jpg) | 3. LRS-instruktionen Vi är nu mogna att i detalj följa LRS-instruktionen (ladda register från dataminnet). Vi ska göra detta i tre steg. Först ska vi studera den typ |
| [48 / PDF 55](../bookpages/Page_054.jpg) | Fig 4,9 visar några viktiga tidsdiagram för instruktionen LRS. Dia- grammen är uppdelade på tre faser och varje fas har åtta deltider mar- |
| [49 / PDF 56](../bookpages/Page_055.jpg) | Fig 4.9 Tidsdiagram för instruktionen LRS (LRS = läs från dataminnet) Streckad pil anger när data avläses, dvs krav på "data valid" |
| [50 / PDF 57](../bookpages/Page_056.jpg) | LRS är en tvåordsinstruktion. Dess instruktionsformat är som vi tidi- gare sett följande |
| [50 / PDF 57](../bookpages/Page_056.jpg) | Exekveringen av en LRS-instruktion tar tre faser (maskincykler) eller 24 deltider i anspråk. |
| [50 / PDF 57](../bookpages/Page_056.jpg) | Instruktionen avkodas nu och detta leder till en exekvering som för instruktionen LRS tar ytterligare två faser i anspråk (execute). |
| [50 / PDF 57](../bookpages/Page_056.jpg) | Vid början av tid T6 i fas 1 läggs nästa adress ut på AB. Eftersom instruktionen LRS avser hämtning av data i dataminnet måste den nya adressen på AB peka ut den önskade platsen i dataminnet (OPRADR = |
| [51 / PDF 58](../bookpages/Page_057.jpg) | hämtningsfas som är lika för alla instruktioner. Låt oss därför börja med att i detalj följa upp fas f för LRS-instruktionen. |
| [51 / PDF 58](../bookpages/Page_057.jpg) | Fig 4,10a visar förloppen under de åtta deltiderna av fas $ för instruk- tionen LRS. Vi kan följa dessa förlopp i detalj på schemat i fig 4.1. |
| [51 / PDF 58](../bookpages/Page_057.jpg) | som PME-signalen på kontrollbussen avslutas. Operationsko- den tolkas som tvåordsinstruktionen LRS. Nu har vi alltså följt operationerna i CMC8 och kontrollerat att inga |
| [52 / PDF 59](../bookpages/Page_058.jpg) | 08 19 Fig 4.10 Fas ff (fetch) för instruktionen LRS a) Funktioner |
| [53 / PDF 60](../bookpages/Page_059.jpg) | 3.3 Mikroprogram för LRS-instruktionen |
| [53 / PDF 60](../bookpages/Page_059.jpg) | Fig 4.11 visar mikroprogrammet för samtliga tre faser av LRS-in- struktionen. För att få grindnätet för timing så enkelt som möjligt har |
| [53 / PDF 60](../bookpages/Page_059.jpg) | Fig 4.12 ger en principiell lösning till MOP-signaleringen för LRS- instruktionen. |
| [53 / PDF 60](../bookpages/Page_059.jpg) | SMEZ SMEN —Ff Fig 4.11 LRS-instruktionens mikroprogram |
| [54 / PDF 61](../bookpages/Page_060.jpg) | Ö LRS-instruktionens MOP:ar |
| [54 / PDF 61](../bookpages/Page_060.jpg) | 3.4 Skillnaden mellan LRS och SRS |
| [54 / PDF 61](../bookpages/Page_060.jpg) | Fig 4.13 visar tidsdiagrammen för instruktionen SRS (store into storage memory). Den skiljer sig från LRS-instruktionen i följande väsentliga avseenden. |
| [56 / PDF 63](../bookpages/Page_062.jpg) | Vi har tidigare sett att även EXECUTE kan innehålla minneshämt- ningar (exempelvis i fas 1 och fas 2 hos LRS-instruktionen). Även dessa hämtningar kan utnyttja MEMR-kontrollen. Detta är underför- |
| [58 / PDF 65](../bookpages/Page_064.jpg) | I fig 4.16 återges LRS-instruktionens tidsdiagram (från fig 4.9) med denna gång med en WAIT-cykel för varje minneshämtning. Enligt dia- |
| [60 / PDF 67](../bookpages/Page_066.jpg) | I fig 4.17 återges LRS-instruktionens tidsdiagram från fig 4.9 men denna gång inkommer en HALT-signal före tidpunkten FÖT3. Vi ser |
| [60 / PDF 67](../bookpages/Page_066.jpg) | med att hoppa tillbaka till det avbrutna arbetet i fas Ff/ och deltid T4, varefter LRS-instruktionen fullbordas. |
| [67 / PDF 74](../bookpages/Page_073.jpg) | LARM 0 1000RRR / ADR/ 3 LOAD FROM PROGRAM MEMORY. LRS 010 10RRR /ADR/ 3 LOAD FROM STORAGE MEMORY. LRX 0 1001RRR 3 LOAD FRUM PROGRAM MEMORY |
| [68 / PDF 75](../bookpages/Page_074.jpg) | Den tidigare behandlade instruktionen LRS (ladda register R från min- net) är en tvåordsinstruktion med formatet e. Första ordet innehåller |
| [69 / PDF 76](../bookpages/Page_075.jpg) | 2. Exekveringstid LRS-instruktionen, som vi studerat tidigare, tar 3 cykler (eller faser) i anspråk för exekvering. Olika instruktioner har olika lång exekverings- |
| [69 / PDF 76](../bookpages/Page_075.jpg) | tioner, exempelvis BT och BZ, tar två cykler i anspråk. De tvåords- instruktioner som skriver till eller läser från minnet (som LRS) tar tre cykler i anspråk. |
| [72 / PDF 79](../bookpages/Page_078.jpg) | Fetchfasen är densamma som för LRS (fig 4.10). Fas 1 och fas 2 fram- går av fig 5.6. Observera att MOP (22) vid F2T6 i detta fall ställs av |
| [119 / PDF 126](../bookpages/Page_125.jpg) | Vi har tidigare ingående studerat exekveringen av de två instruktionerna LRS Load from storage memory (fig 4. 9) JMP Jump to /ADR/ page PP (fig 5. 3). |
| [119 / PDF 126](../bookpages/Page_125.jpg) | visar en närbild av DIP -switcharnas inställning. För LRS-instruktionen har vi valt register 3 som ackumulator och minnesadressen |
| [119 / PDF 126](../bookpages/Page_125.jpg) | POSITION MEMO OK TÄT. dd LRS 123 1 /ADR/ 125 |
| [121 / PDF 128](../bookpages/Page_127.jpg) | För programmets exekvering åtgår 5 maskincykler: Hämta LRS Hämta /ADR/ |
| [121 / PDF 128](../bookpages/Page_127.jpg) | Hämta /ADR/ Exekvera LRS Hämta JMP |
| [121 / PDF 128](../bookpages/Page_127.jpg) | Maskincykel 1: Hämta LRS |
| [122 / PDF 129](../bookpages/Page_128.jpg) | LRS = läs från dataminnet |
| [122 / PDF 129](../bookpages/Page_128.jpg) | Fig 7.11 LRS-instruktionens mikroprogram och tidsdiagram |
| [124 / PDF 131](../bookpages/Page_130.jpg) | Maskincykel 3: Exekvera LRS |
| [125 / PDF 132](../bookpages/Page_131.jpg) | Maskincykel 1: Hämta LRS |
| [125 / PDF 132](../bookpages/Page_131.jpg) | o Skriv in talet i minnet (SRM eller SRS) o Läs ut talet från minnet (LRM eller LRS) o Hoppa tillbaka (JMP) |
| [126 / PDF 133](../bookpages/Page_132.jpg) | 3 /ADR/ adress 3 /ADR/ adress 4 LRM 103 4 LRS 123 5 /ADR/ adress 5 SADR/ adress |
| [217 / PDF 224](../bookpages/Page_223.jpg) | bulfert 20; 27 dual in line 166 INTE 62 logisk operation 16 burn in 169 D-vippa 8 interface 92 LRS 54 buss 25 D2 109 interrupt 60, 105 LRS-instruktion 48 |
| [217 / PDF 224](../bookpages/Page_223.jpg) | burn in 169 D-vippa 8 interface 92 LRS 54 buss 25 D2 109 interrupt 60, 105 LRS-instruktion 48 interrupt acknowledge L-vippa 74 |

## LRX

Patterns: `LRX`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | LRS 010 10RRR /ADR/ 3 LOAD FROM STORAGE MEMORY. LRX 0 1001RRR 3 LOAD FRUM PROGRAM MEMORY ADDRESSED BY X-REGISTER. |
| [155 / PDF 162](../bookpages/Page_161.jpg) | 053 /ED1/ 081 054 LRX, 5 M(X)— R5 135 (55 SRD, 5 R5— datareg 035 |

## LSX

Patterns: `LSX, ESX`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [40 / PDF 47](../bookpages/Page_046.jpg) | LSX = load from storage memory adressed by X-register. |
| [43 / PDF 50](../bookpages/Page_049.jpg) | Som tidigare nämnts kan register R7 användas för adressering. Instruk- tionen LSX (load from storage memory addressed by X-register) är en enordsinstruktion som förutsätter att en adress finns i X-registret |
| [43 / PDF 50](../bookpages/Page_049.jpg) | enordsinstruktion som förutsätter att en adress finns i X-registret (indexed addressing). LSX borde därmed vara snabbare än LRS som är en tvåordsinstruktion. I CMC8 tar emellertid båda dessa instruktioner |
| [67 / PDF 74](../bookpages/Page_073.jpg) | ADDRESSED BY X-REGISTER. ESX O10711RRR 3 LUAD FROM STORAGE MEMORY ADDRESSED BY X-REGISTER. |
| [151 / PDF 158](../bookpages/Page_157.jpg) | ning till indexregistret R7. Nu kan innehållet på denna adress läsas in till R5 med indexerad adressering (LSX, 5 = ladda reg R5 med in- nehållet i den cell som utpekas av indexregistret R7). Register R5 |

## LRD

Patterns: `LRD`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | ADDRESSED BY X-REGISTER. LRD 000 10RARR /ADR/ 3 LOAD FROM EXTERNAL DEVICE. SAM 01100RRR / ADR / 3 STORE INTO PROGRAM MEMORY. |
| [93 / PDF 100](../bookpages/Page_099.jpg) | SRD gpg kör ut styrsignalen HT LRD 091 hämta in svar från port g$g1 |
| [94 / PDF 101](../bookpages/Page_100.jpg) | Instruktionen LRD gg1 (load into ackumulator from external device) hämtar in insignalerna från inporten 1 till ackumulatorn. Men det är |
| [126 / PDF 133](../bookpages/Page_132.jpg) | Ö LRD Load from external device \| 023 i /JADR/ 003 |
| [127 / PDF 134](../bookpages/Page_133.jpg) | POS MEMO OKTAL FÖRKLARING Ö LRD 023 2 /ADR/ 683 |
| [128 / PDF 135](../bookpages/Page_134.jpg) | g LRD $23 il /ADR/ 003 |
| [129 / PDF 136](../bookpages/Page_135.jpg) | POS MEMO OKTAL FÖRKLARING g LRD 023 läs 1 /ADR/ gg2 adress till ED2 |
| [153 / PDF 160](../bookpages/Page_159.jpg) | Läs KB Dog LRD, 6 026 [ 1as Ke pöl — /ED5/ $85 |
| [153 / PDF 160](../bookpages/Page_159.jpg) | RÖ RT PAT TI NOR Ta \| 7 R1 010 LRD, 7 g27 g11 /ED5/ 085 |
| [155 / PDF 162](../bookpages/Page_161.jpg) | $47 LRD, 7 Adressreg— R7 Ög27 250 /ED1/ gg1 |

## SRM

Patterns: `SRM, SAM`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | LRD 000 10RARR /ADR/ 3 LOAD FROM EXTERNAL DEVICE. SAM 01100RRR / ADR / 3 STORE INTO PROGRAM MEMORY. SRS 01110RRR /ADR/ 3 STORE INTO STORAGE MEMORY. |
| [77 / PDF 84](../bookpages/Page_083.jpg) | RRL slutligen skiftar R(A) ett steg åt höger men bit I skiftas in i den linkvippa vi tidigare omnämnt i samband med villkorliga hopp. Sam- tidigt skiftas linkvippans tidigare värde över till bit 7. |
| [125 / PDF 132](../bookpages/Page_131.jpg) | av databussen in till instruktionsregistret IR. FÖT6 PME slocknar och innehållet på databussen försvinner. Sam- tidigt läggs nya programräknaren ut på adressbussen (9093). |
| [125 / PDF 132](../bookpages/Page_131.jpg) | o Lägg ett tal i ackumulatorn (R3) med instruktionen LRI o Skriv in talet i minnet (SRM eller SRS) o Läs ut talet från minnet (LRM eller LRS) |
| [126 / PDF 133](../bookpages/Page_132.jpg) | 1 /DATA/ data i (DATA data 2 SRM 143 Z SRS 163 3 /ADR/ adress 3 /ADR/ adress |
| [126 / PDF 133](../bookpages/Page_132.jpg) | kortet kommer register 3 (RRR = (11) att laddas med det ord vi ställt in i position 1. Detta ord skrivs (SRM) sedan in till den adress i pro- gramminnet som är inställd på position 3. Om samma adress åter- |
| [190 / PDF 197](../bookpages/Page_196.jpg) | I nära anslutning till datorn finns en trumplotter av typ Calcomp 936. Det är ritningar från denna plotter vi tidigare sett exempel på i sam- band med beskrivningen av CMC8. För fotomaskgenereringen används |
| [190 / PDF 197](../bookpages/Page_196.jpg) | en Sentry 7. De är medelstora datorer som är försedda med flera teststationer där kretsar med upp till 60 anslutningar kan testas sam- tidigt oberoende av varandra. Testprogram skrivs i ett Algol-liknande |
| [208 / PDF 215](../bookpages/Page_214.jpg) | När simuleringsresultaten blivit godtagbara gör man en cellayout som efterliknar simuleringens komponentdimensioner så långt möjligt. Sam- tidigt vill man minimera cellens storlek och göra det så lätt som möj- |

## SRS

Patterns: `SRS`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [front/back / PDF 5](../bookpages/Page_004.jpg) | 3 .3 Mikroprogram för LRS-instruktionen 53 3 4 Skillnaden mellan LRS och SRS 54 4 Tillståndsdiagram 55 |
| [54 / PDF 61](../bookpages/Page_060.jpg) | 3.4 Skillnaden mellan LRS och SRS |
| [54 / PDF 61](../bookpages/Page_060.jpg) | Fig 4.13 visar tidsdiagrammen för instruktionen SRS (store into storage memory). Den skiljer sig från LRS-instruktionen i följande |
| [55 / PDF 62](../bookpages/Page_061.jpg) | Fig 4.13 Tidsdiagram för instruktionen SRS (SRS = skriv till data- \| minne) |
| [67 / PDF 74](../bookpages/Page_073.jpg) | SAM 01100RRR / ADR / 3 STORE INTO PROGRAM MEMORY. SRS 01110RRR /ADR/ 3 STORE INTO STORAGE MEMORY. SRX 0 1101RRR S STORE INTO PROGRAM MEMORY |
| [125 / PDF 132](../bookpages/Page_131.jpg) | o Lägg ett tal i ackumulatorn (R3) med instruktionen LRI o Skriv in talet i minnet (SRM eller SRS) o Läs ut talet från minnet (LRM eller LRS) |
| [126 / PDF 133](../bookpages/Page_132.jpg) | 1 /DATA/ data i (DATA data 2 SRM 143 Z SRS 163 3 /ADR/ adress 3 /ADR/ adress |
| [139 / PDF 146](../bookpages/Page_145.jpg) | Biväg \| 0 TI ERSÄRSNESSRA SRS SRS Oo I Oo oil Str lj Np ft |
| [218 / PDF 225](../bookpages/Page_224.jpg) | programvara 136 source 2 utvärdering 195 NAND-grind 4 programverk 44 SRS 54 N-kanaltransistor 2 PROM 115 stapelfel 171 wafer 179 |

## SRX

Patterns: `SRX`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | SRS 01110RRR /ADR/ 3 STORE INTO STORAGE MEMORY. SRX 0 1101RRR S STORE INTO PROGRAM MEMORY ADDRESSED BY X-REGISTER. |

## SSX

Patterns: `SSX`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | ADDRESSED BY X-REGISTER. SSX 0171718RR 3 STORE INTO STORAGE MEMORY ADDRESSED BY X-REGISTER. |
| [68 / PDF 75](../bookpages/Page_074.jpg) | Enordsinstruktionen SSX (skriv i dataminnet på den adress som anges av X-registret) har detta format. De tre minst signifikanta bitarna i |

## SRD

Patterns: `SRD`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | ADDRESSED BY X-REGISTER. SRD 000 11RRR /ADR/ 3 STORE INTO EXTERNAL DEVICE. BBO 110 10RRR / ADR/ 3 BRANCH IF LEAST SIGNIFICANT BIT |
| [93 / PDF 100](../bookpages/Page_099.jpg) | SRD gpg kör ut styrsignalen HT LRD 091 hämta in svar från port g$g1 |
| [94 / PDF 101](../bookpages/Page_100.jpg) | Instruktionen SRD g0g (store into external device) sänder ackumula- torns innehåll pg4 till utenhetens latch. Och därmed tänds lampan |
| [126 / PDF 133](../bookpages/Page_132.jpg) | i /JADR/ 003 2 SRD Store into external device 033 3 /ADR/ pp4 |
| [127 / PDF 134](../bookpages/Page_133.jpg) | 2 /ADR/ 683 2 SRD 033 3 /ADR/ Ö06 kontrollportens adress |
| [128 / PDF 135](../bookpages/Page_134.jpg) | il /ADR/ 003 2 SRD 033 3 SADR/ Ögg, BB1 eller $$2 |
| [129 / PDF 136](../bookpages/Page_135.jpg) | 1 /ADR/ gg2 adress till ED2 2 SRD 033 skriv 3 /ADR/ 01 adress till ED1 |
| [129 / PDF 136](../bookpages/Page_135.jpg) | 1 /ADR/ 005 ED5 = tangentbord 2 SRD 033 skriv 3 (ADR / 082 ED2 = displayen till höger |
| [146 / PDF 153](../bookpages/Page_152.jpg) | 281 /Ljustyp $/ ; 266 gg2 SRD, 3 rija 033 $p3 /ED4/ gp4 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | 013 /Ljustyp 1/ Ö67 g14 SRD, 3 NOD 33 015 /ED4/ p04 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | g21 /Ljustyp 2/ : 070 g22 SRD, 3 IEND p33 (23 /ED4/ 004 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | $31 /Ljustyp 3/ Ö71 p32 SRD, 3 ESD 933 033 /ED4/ pp4 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | 43 /Ljustyp 4/ ; Ö72 f44 SRD, 3 FJUSDD g33 f45 /ED4/ 004 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | 053 /Ljustyp 2/ : gp $54 SRD, 3 SEDD g33 $55 /ED4/ P4 |
| [147 / PDF 154](../bookpages/Page_153.jpg) | g61 /Ljustyp $/ 266 062 SRD, 3 Re a 033 263 /ED4/ pg4 |
| [150 / PDF 157](../bookpages/Page_156.jpg) | g22 + 374 ÖR -— 374 g23 SRD, 2 Mölsnres ; 032 g24 /ED6/ minnesmo Bg6 |
| [155 / PDF 162](../bookpages/Page_161.jpg) | 051 INR, 7 Inkrementera 207 p52 SRD, I R7— adressreg p32 053 /ED1/ 081 |
| [155 / PDF 162](../bookpages/Page_161.jpg) | 054 LRX, 5 M(X)— R5 135 (55 SRD, 5 R5— datareg 035 056 £ED2/ och display Ög2 |

## BB0

Patterns: `BB\s*[0OØøÖö$g&fS]`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | SRD 000 11RRR /ADR/ 3 STORE INTO EXTERNAL DEVICE. BBO 110 10RRR / ADR/ 3 BRANCH IF LEAST SIGNIFICANT BIT OF REGISTER = 0. |
| [70 / PDF 77](../bookpages/Page_076.jpg) | o minst signifikanta biten i register R(A), (BBS, BB1) o linkvippans ställning, (BL$, BL1) |
| [72 / PDF 79](../bookpages/Page_078.jpg) | Låt oss följa ett mikroprogram för villkorligt hopp! Vi väljer BBf$, dvs hoppa om minst signifikanta biten av R(A) är noll. |
| [73 / PDF 80](../bookpages/Page_079.jpg) | BBf = hopp om bit g = 0 |
| [73 / PDF 80](../bookpages/Page_079.jpg) | 63) Fig 5.6 Exempel på mikroinstruktion för villkorligt hopp, BBf (hopp om minst signifikanta biten är noll, BA = bit $) |
| [154 / PDF 161](../bookpages/Page_160.jpg) | 035 BBf, 6 Udda? 326 036 /sifferrutin/ — sifferident. 365 |
| [154 / PDF 161](../bookpages/Page_160.jpg) | g41 SHR, 6 Högerskift 226 042 BBf(, 6 Udda? 320 43 /DA eller GO/ — "DA eller GO" 112 |
| [154 / PDF 161](../bookpages/Page_160.jpg) | $44 SHR, 6 Högerskift 226 045 BBf, 6 Udda? JA0 646 /AD/ — AD-rutin 061 |

## BB1

Patterns: `BB\s*1`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | OF REGISTER = 0. BB1 110 11RR8R / ADR/ 3 BRANCH IF LEAST SIGNIFICANT BIT OF REGISTER = 1. |
| [70 / PDF 77](../bookpages/Page_076.jpg) | o minst signifikanta biten i register R(A), (BBS, BB1) o linkvippans ställning, (BL$, BL1) |
| [128 / PDF 135](../bookpages/Page_134.jpg) | 2 SRD 033 3 SADR/ Ögg, BB1 eller $$2 4 JMP 360 |

## BL0

Patterns: `BL\s*[0OØøÖö$g&fS]`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [61 / PDF 68](../bookpages/Page_067.jpg) | 2 SV L SVIT 2 Svs ke LIVM - DD SVIT ZIG Le LLC HET LL 9 GET LÄ IG HET BLS GRE LO IG ec 2 LA |
| [67 / PDF 74](../bookpages/Page_073.jpg) | OF REGISTER = 1. BLO 111001PP / ADR/ 2 BRANCH TO PAGE PP IF LINK = Öd. BL 1 111011PP / ADR/ A BRANCH TO PAGE PP IF LINK = 1. |
| [70 / PDF 77](../bookpages/Page_076.jpg) | o minst signifikanta biten i register R(A), (BBS, BB1) o linkvippans ställning, (BL$, BL1) o nollvippans ställning, (BZ$, BZ1) |

## BL1

Patterns: `BL\s*1`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | BLO 111001PP / ADR/ 2 BRANCH TO PAGE PP IF LINK = Öd. BL 1 111011PP / ADR/ A BRANCH TO PAGE PP IF LINK = 1. BZ0 111000PP /ADR/ 2 BRANCH TO PAGE PP IF ZFLAG = 0. |
| [70 / PDF 77](../bookpages/Page_076.jpg) | o minst signifikanta biten i register R(A), (BBS, BB1) o linkvippans ställning, (BL$, BL1) o nollvippans ställning, (BZ$, BZ1) |

## BZ0

Patterns: `BZ\s*[0OØøÖö$g&fS]`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | BL 1 111011PP / ADR/ A BRANCH TO PAGE PP IF LINK = 1. BZ0 111000PP /ADR/ 2 BRANCH TO PAGE PP IF ZFLAG = 0. BZ1 111010PP / ADR/ 2 BRANCH TO PAGE PP IF ZFLAG = 1. |
| [70 / PDF 77](../bookpages/Page_076.jpg) | o linkvippans ställning, (BL$, BL1) o nollvippans ställning, (BZ$, BZ1) o signal på testingång, (BTf$, BT1) |
| [93 / PDF 100](../bookpages/Page_099.jpg) | ANI 091g maska av bit 3 BZ$ HIT hoppa tillbaka till HIT om Z = 0 |
| [95 / PDF 102](../bookpages/Page_101.jpg) | lar Z-flaggan (se fig 5.1) och om ackumulatorns värde + 0 blir Z = 0. Instruktionen BZ gör i detta fall ett hopp till adressen med etiketten HIT. CMC8 ligger alltså i en slinga (loop) och avvaktar att lampan ska |
| [148 / PDF 155](../bookpages/Page_154.jpg) | GL DCR, 6 146 126 BZf 34f 121 /LOOP/ 115 |

## BZ1

Patterns: `BZ\s*1`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | BZ0 111000PP /ADR/ 2 BRANCH TO PAGE PP IF ZFLAG = 0. BZ1 111010PP / ADR/ 2 BRANCH TO PAGE PP IF ZFLAG = 1. BTO 1140000TT /ADR/ 2 BRANCHSTIE TEST INPUT (TT)-= 00: |
| [70 / PDF 77](../bookpages/Page_076.jpg) | o linkvippans ställning, (BL$, BL1) o nollvippans ställning, (BZ$, BZ1) o signal på testingång, (BTf$, BT1) |

## BT0

Patterns: `BT\s*[0OØøÖö$g&fS]`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | BZ1 111010PP / ADR/ 2 BRANCH TO PAGE PP IF ZFLAG = 1. BTO 1140000TT /ADR/ 2 BRANCHSTIE TEST INPUT (TT)-= 00: BA 110010TT / ADR/ 2 BRANDE IE TEST INEUT SÄ TI) = St: |
| [70 / PDF 77](../bookpages/Page_076.jpg) | o nollvippans ställning, (BZ$, BZ1) o signal på testingång, (BTf$, BT1) |
| [105 / PDF 112](../bookpages/Page_111.jpg) | som kan användas som hoppvillkor. Man kan därför med enkla instruk- tioner (BTf$ resp BT1 i fig 5.1) direkt avkänna fyra ledningar. Se fig 6:22. |

## BT1

Patterns: `BT\s*1, BTL, BIL`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [70 / PDF 77](../bookpages/Page_076.jpg) | o nollvippans ställning, (BZ$, BZ1) o signal på testingång, (BTf$, BT1) |
| [105 / PDF 112](../bookpages/Page_111.jpg) | som kan användas som hoppvillkor. Man kan därför med enkla instruk- tioner (BTf$ resp BT1 i fig 5.1) direkt avkänna fyra ledningar. Se fig 6:22. |
| [106 / PDF 113](../bookpages/Page_112.jpg) | grammet. På order av programmet exekveras instruktionerna BT el- ler BT1 och därvid avkänner processorn testsignaler. Vissa signaler (hög eller låg) leder till subrutinhopp och därmed till åtgärder. |
| [140 / PDF 147](../bookpages/Page_146.jpg) | T2 och T3 avbilda givarna. (När vi i vår modell vill simulera att en bil på bivägen närmar sig korsningen från väster trycker vi alltså på T3). |
| [145 / PDF 152](../bookpages/Page_151.jpg) | 005 /FRAM/ 206 BTL, 3 007 /FRAM/ |
| [146 / PDF 153](../bookpages/Page_152.jpg) | $p3 /ED4/ gp4 HIT 604 BIL i 311 005 /FRAM/ 612 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | 005 /FRAM/ 612 006 BIL 3 313 BOT /FRAM/ 2 Nr g12 |

## JMP

Patterns: `JMP`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [31 / PDF 38](../bookpages/Page_037.jpg) | rekt och som därför endast tar en cykel i anspråk. Det finns också instruktioner (exempelvis JMP, ovillkorligt hopp) som har en hämt- ningsfas och en exekveringsfas och därmed upptar totalt 2 cykler. |
| [42 / PDF 49](../bookpages/Page_048.jpg) | ta bitar. För sidbyte kan man bl a använda den tidigare omnämnda in- struktionen JMP (ovillkorligt hopp) som upptar två cykler och har for- matet |
| [42 / PDF 49](../bookpages/Page_048.jpg) | matet I Til 00 PP JMP |
| [67 / PDF 74](../bookpages/Page_073.jpg) | BA 110010TT / ADR/ 2 BRANDE IE TEST INEUT SÄ TI) = St: JMP 111100PP / ADR/ 2 JUMP TO /ADR/ PAGE PP JCR 111118RR 2 JUMP TO CONTENT OF REGISTER. |
| [69 / PDF 76](../bookpages/Page_075.jpg) | CMC8 har ett tiotal hoppinstruktioner. Av dessa är JMP, JCR och JSR ovillkorliga hopp. |
| [70 / PDF 77](../bookpages/Page_076.jpg) | fordras att programräknarens innehåll ändras till den önskade hoppad- ressen. Vid JMP anger andra ordet hoppadressen och bitarna & och 1 i första ordet anger den sida (page) till vilket hoppet ska ske. Vid JCR |
| [70 / PDF 77](../bookpages/Page_076.jpg) | Vi kan följa JMP-instruktionens mikroprogram i fig 4.1 med hjälp av fig 5.3. Under fas F$ hämtas instruktionen på samma sätt som vi tidi- |
| [70 / PDF 77](../bookpages/Page_076.jpg) | JMP = ovillkorligt hopp Tf TI 2 T3 T4 T5 T6 TÅ |
| [70 / PDF 77](../bookpages/Page_076.jpg) | & 19 12 8 vv \|G Fig 5.3 Mikroprogram för fas 1 och 2 hos instruktionen JMP (ovillkorligt hopp) |
| [71 / PDF 78](../bookpages/Page_077.jpg) | Eftersom JMP kan exekveras på två cykler inkrementeras fasräknaren vid tiden F1T1 och mikroprogrammet hoppar därför direkt till fas 2. |
| [71 / PDF 78](../bookpages/Page_077.jpg) | Mikroprogrammet för JMP är som framgår av fig 5.3 mycket enkelt. De övriga ovillkorliga hoppinstruktionerna är uppbyggda på liknande |
| [89 / PDF 96](../bookpages/Page_095.jpg) | Låt oss slutligen följa SS-funktionen i tidsdiagrammet vid exekveringen av en enkel instruktion. Vi väljer här JMP, dvs ovillkorligt hopp, som vi tidigare behandlat i fig 5.3. |
| [89 / PDF 96](../bookpages/Page_095.jpg) | Tidsdiagrammet för JMP framgår av fig 6.7. Under fas F9 hämtas instruktion och under fas F1 inkrementeras fasräknaren och maskin- |
| [90 / PDF 97](../bookpages/Page_096.jpg) | I fig 6.8 ser vi vad som inträffar när instruktionen JMP exekveras med SS-kontrollen. |
| [90 / PDF 97](../bookpages/Page_096.jpg) | Kod för Hopp - JMP adress |
| [90 / PDF 97](../bookpages/Page_096.jpg) | Fig 6.7 Tidsdiagram för instruktionen JMP |
| [91 / PDF 98](../bookpages/Page_097.jpg) | Fig 6.8 Tidsdiagram för instruktionen JMP exekverad med single step |
| [119 / PDF 126](../bookpages/Page_125.jpg) | LRS Load from storage memory (fig 4. 9) JMP Jump to /ADR/ page PP (fig 5. 3). Låt oss "knappa in" dessa två instruktioner på PROM-kortet. Fig 7.10 |
| [119 / PDF 126](../bookpages/Page_125.jpg) | 1 /ADR/ 125 2 JMP 360 3 /ADR/ 000 |
| [121 / PDF 128](../bookpages/Page_127.jpg) | Exekvera LRS Hämta JMP Hämta /ADR/ och exekvera samtidigt JMP: |
| [121 / PDF 128](../bookpages/Page_127.jpg) | Hämta JMP Hämta /ADR/ och exekvera samtidigt JMP: |
| [124 / PDF 131](../bookpages/Page_130.jpg) | Maskincykel 4: Hämta JMP (jämför med Ff i fig 7.11) |
| [125 / PDF 132](../bookpages/Page_131.jpg) | STA fas och på databussen ligger oktalt 360, dvs instruktionen JMP (till sida Pg). FfÖT5 Ingen yttre förändring, men vid slutet av T5 lästes innehållet |
| [125 / PDF 132](../bookpages/Page_131.jpg) | Maskincykel 5: Hämta /ADR/ och exekvera JMP (Jämför med fig 5. 3 och 6. 7) |
| [125 / PDF 132](../bookpages/Page_131.jpg) | o Läs ut talet från minnet (LRM eller LRS) o Hoppa tillbaka (JMP) |
| [126 / PDF 133](../bookpages/Page_132.jpg) | 5 /ADR/ adress 5 SADR/ adress 6 JMP 360 6 JMP 360 7 ZADR/ adress T /ADR/ adress |
| [126 / PDF 133](../bookpages/Page_132.jpg) | 3 /ADR/ pp4 4 JMP Jump to /ADR/ page PP 360 5 /ADR/ 000 |
| [127 / PDF 134](../bookpages/Page_133.jpg) | 3 /ADR/ Ö06 kontrollportens adress 4 JMP 360 5 (ÄNDRA 006 |
| [128 / PDF 135](../bookpages/Page_134.jpg) | 3 SADR/ Ögg, BB1 eller $$2 4 JMP 360 5 /ADR/ VAN |
| [129 / PDF 136](../bookpages/Page_135.jpg) | 3 /ADR/ 01 adress till ED1 4 JMP 360 återhopp 5 /ADR/ BOD |
| [129 / PDF 136](../bookpages/Page_135.jpg) | 3 (ADR / 082 ED2 = displayen till höger 4 JMP 360 åter- 5 /ADR/ 000 hopp |
| [135 / PDF 142](../bookpages/Page_141.jpg) | dvs hopp (JMP) till sida 3. |
| [145 / PDF 152](../bookpages/Page_151.jpg) | 007 /FRAM/ 016 JMP g11 /HIT/ |
| [146 / PDF 153](../bookpages/Page_152.jpg) | BOT /FRAM/ 2 Nr g12 010 JMP SN 360 g11 /HIT/ pg4 |
| [147 / PDF 154](../bookpages/Page_153.jpg) | 263 /ED4/ pg4 064 JMP o 360 $65 /HIT/ Aterhopp Öga |
| [148 / PDF 155](../bookpages/Page_154.jpg) | 121 /LOOP/ 115 122 JMP 360 123 /HIT/ P4 |
| [150 / PDF 157](../bookpages/Page_156.jpg) | ADRESS MEMO-KOD = KOMMENTAR MASKINKOD 363 JMP, 3 Hoppa 363 364 /ADR/ vidare g17 |
| [152 / PDF 159](../bookpages/Page_158.jpg) | RÖ PC 316" JMP P1 |
| [155 / PDF 162](../bookpages/Page_161.jpg) | 056 £ED2/ och display Ög2 Ö57 JMP Återhopp 363 p6f6 /LOOP/ 033 |

## JCR

Patterns: `JCR`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | JMP 111100PP / ADR/ 2 JUMP TO /ADR/ PAGE PP JCR 111118RR 2 JUMP TO CONTENT OF REGISTER. LETI 00 100RRR /DATA/ 2 LOAD REGISTER IMMEDIATE. |
| [69 / PDF 76](../bookpages/Page_075.jpg) | CMC8 har ett tiotal hoppinstruktioner. Av dessa är JMP, JCR och JSR ovillkorliga hopp. |
| [70 / PDF 77](../bookpages/Page_076.jpg) | ressen. Vid JMP anger andra ordet hoppadressen och bitarna & och 1 i första ordet anger den sida (page) till vilket hoppet ska ske. Vid JCR tas hoppadressen från det register som anges av bitarna & - 2 (dvs A) |
| [70 / PDF 77](../bookpages/Page_076.jpg) | tas hoppadressen från det register som anges av bitarna & - 2 (dvs A) i JCR-instruktionen (som är en enordsinstruktion). Vid JSR, dvs hopp till subrutin, inkrementeras N-registret och därför |

## LRI

Patterns: `LR\s*I, LETI, TRI`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | JCR 111118RR 2 JUMP TO CONTENT OF REGISTER. LETI 00 100RRR /DATA/ 2 LOAD REGISTER IMMEDIATE. XRI O0101ARRR /DATA/ FÅ 3 EXCLUSIVE OR IMMEDIATE. |
| [68 / PDF 75](../bookpages/Page_074.jpg) | Formatc Instruktionen LRI (ladda register direkt, load register immediate) är en tvåordsinstruktion och har format c. Här ligger data i andra ordet |
| [93 / PDF 100](../bookpages/Page_099.jpg) | LRI 094 ladda styrsignal till port ggg |
| [94 / PDF 101](../bookpages/Page_100.jpg) | ar 0): Programsekvensen börjar med en LRI-instruktion (load immediate) som lägger talet $Pp4 i ackumulatorn: |
| [125 / PDF 132](../bookpages/Page_131.jpg) | o Lägg ett tal i ackumulatorn (R3) med instruktionen LRI o Skriv in talet i minnet (SRM eller SRS) |
| [126 / PDF 133](../bookpages/Page_132.jpg) | Ö LRI 043 g LRI 043 1 /DATA/ data i (DATA data |
| [131 / PDF 138](../bookpages/Page_137.jpg) | Outputs are enabled when valid entry is made and go into TRI-STATE when key is released. |
| [143 / PDF 150](../bookpages/Page_149.jpg) | 1 00 g0g 2 LRI, 4 \| 5 $44 3 3 20:04 XXX |
| [147 / PDF 154](../bookpages/Page_153.jpg) | 181 =000 Bo 102 TRI i p44 103 +172 (dec 76) TR |
| [148 / PDF 155](../bookpages/Page_154.jpg) | ETIKETT ADRESS <MEMO-KOD MASKINKOD LÅNG 113 LRI, 6 g46 114 = 033 p33 |
| [150 / PDF 157](../bookpages/Page_156.jpg) | 020 + 201 lampan 261 021 TRI, 2 S g42 g22 + 374 ÖR -— 374 |
| [154 / PDF 161](../bookpages/Page_160.jpg) | 036 /sifferrutin/ — sifferident. 365 037 LRI, 4 $— positions- g44 ET + 00 räknare 000 |
| [214 / PDF 221](../bookpages/Page_220.jpg) | [ fuse LR I EE firar = [ ct N 1 I = MN ea EN |

## XRI

Patterns: `XR\s*I`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | LETI 00 100RRR /DATA/ 2 LOAD REGISTER IMMEDIATE. XRI O0101ARRR /DATA/ FÅ 3 EXCLUSIVE OR IMMEDIATE. ANI O0110RAR /DATA/ Z 3 AND IMMEDIATE. |

## ANI

Patterns: `ANI`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | XRI O0101ARRR /DATA/ FÅ 3 EXCLUSIVE OR IMMEDIATE. ANI O0110RAR /DATA/ Z 3 AND IMMEDIATE. CPY O01118RR 2 COPY REGISTER INTO X-REGISTER. |
| [93 / PDF 100](../bookpages/Page_099.jpg) | ANI 091g maska av bit 3 BZ$ HIT hoppa tillbaka till HIT om Z = 0 |
| [94 / PDF 101](../bookpages/Page_100.jpg) | Ö il d (dvs oktala talet 0198) med instruktionen ANI P18 (AND immediate). |
| [95 / PDF 102](../bookpages/Page_101.jpg) | bit 3 är hög, dvs att lampan ännu inte lyser. ANI-instruktionen samp- lar Z-flaggan (se fig 5.1) och om ackumulatorns värde + 0 blir Z = 0. |

## CPY

Patterns: `CPY`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | ANI O0110RAR /DATA/ Z 3 AND IMMEDIATE. CPY O01118RR 2 COPY REGISTER INTO X-REGISTER. INR 10000ARRR Zz > INCREMENT REGISTER. i |
| [153 / PDF 160](../bookpages/Page_159.jpg) | [ 1as Ke pöl — /ED5/ $85 dg2 — CPY,6 g76 ET 003 XR T $57 |

## INR

Patterns: `INR`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [17 / PDF 24](../bookpages/Page_023.jpg) | gångar (register A och register B), en utgång (register R) samt ett antal styringångar, i vårt exempel INR (för inkrementering), AND, XOR och SH (för skift). |
| [19 / PDF 26](../bookpages/Page_025.jpg) | INR AND -XOR SH |
| [45 / PDF 52](../bookpages/Page_051.jpg) | pekar ut ROM-adresser). Timing kan nu utföras som 24 succesiva in- krementeringar (INR) av adressregistret. Vi startar alltså på en ad- ress som bestäms av instruktionskoden och stegar därefter fram 24 |
| [46 / PDF 53](../bookpages/Page_052.jpg) | INR > V |
| [67 / PDF 74](../bookpages/Page_073.jpg) | CPY O01118RR 2 COPY REGISTER INTO X-REGISTER. INR 10000ARRR Zz > INCREMENT REGISTER. i ROR 1000 18RR 2 ROTATE REGISTER RIGHT. |
| [75 / PDF 82](../bookpages/Page_081.jpg) | vis av 1111g00g). Fig 5.8 ger svar på dessa frågor. Vid inkrementering (INR) används Z-flaggan som carryflagga. Den blir ettställd när binärtalet 11111111 inkrementeras till noll. Z-flaggan |
| [76 / PDF 83](../bookpages/Page_082.jpg) | & e 169 Fig 5.8 Mikroprogram för INR (inkrement) och DCR (dekrement) a) Funktioner |
| [76 / PDF 83](../bookpages/Page_082.jpg) | INR DCR |
| [76 / PDF 83](../bookpages/Page_082.jpg) | INR = inkrementera register DCR = dekrementera register |
| [143 / PDF 150](../bookpages/Page_149.jpg) | 3 3 20:04 XXX INR, 4 INR, 3 3 203 |
| [143 / PDF 150](../bookpages/Page_149.jpg) | INR, 4 INR, 3 3 203 5 BZ \| \| 340 |
| [147 / PDF 154](../bookpages/Page_153.jpg) | 103 +172 (dec 76) TR HOPP 104 INR, 3 203 105 BZ ; 340 |
| [155 / PDF 162](../bookpages/Page_161.jpg) | 250 /ED1/ gg1 051 INR, 7 Inkrementera 207 p52 SRD, I R7— adressreg p32 |

## ROR

Patterns: `ROR`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | INR 10000ARRR Zz > INCREMENT REGISTER. i ROR 1000 18RR 2 ROTATE REGISTER RIGHT. SHR 100 10RRR 2 SHIFT REGISTER RIGHT. |
| [77 / PDF 84](../bookpages/Page_083.jpg) | ROR skiftar R(A) ett steg åt höger men så att bit & skiftas till bit 7 (rotate). |
| [77 / PDF 84](../bookpages/Page_083.jpg) | Re ROR Z 1 |
| [78 / PDF 85](../bookpages/Page_084.jpg) | ledning och in på bit 7 i BR. Kretsen i fig 5.10 utför alltså instruk- tionen ROR (rotate register right). För att exekvera instruktionen SHR behöver vi inte den yttre slingan, |
| [79 / PDF 86](../bookpages/Page_085.jpg) | Fig oli Kretsarna för SHR, ROR och RRL i CMC38 |

## SHR

Patterns: `SHR`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | ROR 1000 18RR 2 ROTATE REGISTER RIGHT. SHR 100 10RRR 2 SHIFT REGISTER RIGHT. RAL 100 11RRR = 2 RUTATE REGISTER THRUUGH LINK. |
| [77 / PDF 84](../bookpages/Page_083.jpg) | skiftande och principen framgår av fig 5. 9. Instruktionen SHR skiftar R(A) ett steg åt höger och skiftar därvid in en nolla i bit 7. |
| [78 / PDF 85](../bookpages/Page_084.jpg) | tionen ROR (rotate register right). För att exekvera instruktionen SHR behöver vi inte den yttre slingan, vi behöver endast ansluta ingång 7 på bufferten till jord (dvs nolla). |
| [79 / PDF 86](../bookpages/Page_085.jpg) | Fig oli Kretsarna för SHR, ROR och RRL i CMC38 |
| [154 / PDF 161](../bookpages/Page_160.jpg) | ET + 00 räknare 000 g41 SHR, 6 Högerskift 226 042 BBf(, 6 Udda? 320 |
| [154 / PDF 161](../bookpages/Page_160.jpg) | 43 /DA eller GO/ — "DA eller GO" 112 $44 SHR, 6 Högerskift 226 045 BBf, 6 Udda? JA0 |

## RRL

Patterns: `RRL, RAL`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | SHR 100 10RRR 2 SHIFT REGISTER RIGHT. RAL 100 11RRR = 2 RUTATE REGISTER THRUUGH LINK. DCR 10 100RRR Z 3 DECREMENT REGISTER. |
| [77 / PDF 84](../bookpages/Page_083.jpg) | RRL slutligen skiftar R(A) ett steg åt höger men bit I skiftas in i den linkvippa vi tidigare omnämnt i samband med villkorliga hopp. Sam- |
| [78 / PDF 85](../bookpages/Page_084.jpg) | Fig 5.12 visar fas 1 och 2 i mikroprogrammet för instruktionen RRL (rotate through link). |
| [79 / PDF 86](../bookpages/Page_085.jpg) | Fig oli Kretsarna för SHR, ROR och RRL i CMC38 |
| [79 / PDF 86](../bookpages/Page_085.jpg) | MBE C Fig 5.12 Mikroprogram för RRL (rotera höger genom link) a) Funktionen |
| [107 / PDF 114](../bookpages/Page_113.jpg) | utgång från linkvippan (LOUT i fig 6. 5). Genom att rotera ett register genom linkvippan (instruktionen RRL upprepad åtta gånger) får man tydligen ut registrets innehåll i serie- |
| [107 / PDF 114](../bookpages/Page_113.jpg) | form på LOUT ( med minst signifikanta biten ut först). Fig 6.25. Om man före varje RRL-instruktion ställer linkvippan i enlighet med signalen på en av testingångarna kan man läsa in seriedata till ett re- |

## DCR

Patterns: `DCR`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | RAL 100 11RRR = 2 RUTATE REGISTER THRUUGH LINK. DCR 10 100RRR Z 3 DECREMENT REGISTER. XOR 1010 18RRR 2 3 EXCLUSIVE OR OF REGISTER AND |
| [76 / PDF 83](../bookpages/Page_082.jpg) | & e 169 Fig 5.8 Mikroprogram för INR (inkrement) och DCR (dekrement) a) Funktioner |
| [76 / PDF 83](../bookpages/Page_082.jpg) | Som framgår av mikroprogrammet i fig 5. 8b använder man för dekre- mentering (DCR) inverteraren (MOP ) från bufferten till inre data- bussen. Under fas 2 inkrementerar man det inverterade värdet. De- |
| [76 / PDF 83](../bookpages/Page_082.jpg) | INR DCR |
| [76 / PDF 83](../bookpages/Page_082.jpg) | INR = inkrementera register DCR = dekrementera register |
| [143 / PDF 150](../bookpages/Page_149.jpg) | 6 /ADR/ ög4 7 DCR, 4 3 244 Ja 10 BZ \| 7 340 |
| [147 / PDF 154](../bookpages/Page_153.jpg) | 186 /HOPP/ SR 104 107 DCR, 4 Mee 244 110 BZ 340 |
| [148 / PDF 155](../bookpages/Page_154.jpg) | 116 /Vänta 10/ 1009 GL DCR, 6 146 126 BZf 34f |

## XOR

Patterns: `XOR`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [17 / PDF 24](../bookpages/Page_023.jpg) | typ som beskrivs i Digitala kretsar (sid 14). En adderare är i princip uppbyggd av AND- och XOR- (kallas ofta EXOR) kretsar. Binär multip- likation med 2 kan utföras som ett skift (aritmetiskt skift). |
| [17 / PDF 24](../bookpages/Page_023.jpg) | Vanliga logiska operationer är AND, OR och XOR. Logiska funktioner används ofta vid "bithantering'", dvs när man i en dator vill manipulera |
| [17 / PDF 24](../bookpages/Page_023.jpg) | de avsökning. Om det tidigare innehållet lagrats undan och sedan jäm- förs (med XOR-funktion) med registrets nya innehåll får man resulta- tet noll om innehållet är oförändrat. Fig 1. 26d. |
| [17 / PDF 24](../bookpages/Page_023.jpg) | antal styringångar, i vårt exempel INR (för inkrementering), AND, XOR och SH (för skift). |
| [18 / PDF 25](../bookpages/Page_024.jpg) | Tidigare ORK XOR [öeO ER Nytt värde [XTXPREX PESEY Gl SV |
| [18 / PDF 25](../bookpages/Page_024.jpg) | Fig 1.26 Exempel på bithantering med hjälp av AND, OR och XOR |
| [19 / PDF 26](../bookpages/Page_025.jpg) | b) AND OR XOR |
| [19 / PDF 26](../bookpages/Page_025.jpg) | INR AND -XOR SH |
| [27 / PDF 34](../bookpages/Page_033.jpg) | inkrementering och skift. CMC8 innehåller de logiska funktionerna AND och XOR samt rotation i två varianter. LSI-kretsen har storleken 35 mm? och innehåller ca 4000 transistorer. Den kan matas med |
| [67 / PDF 74](../bookpages/Page_073.jpg) | DCR 10 100RRR Z 3 DECREMENT REGISTER. XOR 1010 18RRR 2 3 EXCLUSIVE OR OF REGISTER AND X-REGISTER.RESULT TO X REG. |
| [72 / PDF 79](../bookpages/Page_078.jpg) | villkoret kan lagras i en D-vippa (hoppvippan) som får data via en XOR-krets enligt fig 5.5 och som triggas på T2. |
| [74 / PDF 81](../bookpages/Page_080.jpg) | För att nollställa ackumulatorn och samtliga flaggor (utom Z-flaggan) används för 8080 ofta instruktionen XRA A, dvs utför XOR på ackumu- latorns innehåll (med sig själv). Resultatet blir genomgående noll. På |

## AND

Patterns: `AND`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [7 / PDF 14](../bookpages/Page_013.jpg) | visar en vippa bestående av två inverterare. I bipolar teknik används vanligen AND-grindar för vippans klockning. För CMOS-kretsar använ- der man istället transmissionsgrindar. Fig 1.12 visar principen för |
| [11 / PDF 18](../bookpages/Page_017.jpg) | Avkodare i CMOS byggs upp på principiellt samma sätt som i bipolär teknik. Fig 1.18 visar en avkodare som består av fyra AND-grindar. Med två adressingångar (AP och A1) kan vi göra ett val av fyra. Adres- |
| [12 / PDF 19](../bookpages/Page_018.jpg) | Fig 1.18 Avkodare uppbyggd av AND-kretsar (På kristallen utgörs AND-grindarna av NAND-grindar åtföljda av inverterare) |
| [12 / PDF 19](../bookpages/Page_018.jpg) | Fig 1.18 Avkodare uppbyggd av AND-kretsar (På kristallen utgörs AND-grindarna av NAND-grindar åtföljda av inverterare) |
| [16 / PDF 23](../bookpages/Page_022.jpg) | AND- Hd A fö L |
| [16 / PDF 23](../bookpages/Page_022.jpg) | \| Fig 1.25 Aritmetisk logisk enhet och exempel på AND-funktion |
| [17 / PDF 24](../bookpages/Page_023.jpg) | typ som beskrivs i Digitala kretsar (sid 14). En adderare är i princip uppbyggd av AND- och XOR- (kallas ofta EXOR) kretsar. Binär multip- likation med 2 kan utföras som ett skift (aritmetiskt skift). |
| [17 / PDF 24](../bookpages/Page_023.jpg) | Vanliga logiska operationer är AND, OR och XOR. Logiska funktioner används ofta vid "bithantering'", dvs när man i en dator vill manipulera |
| [17 / PDF 24](../bookpages/Page_023.jpg) | En logisk funktion av två variabler utförs i en dator parvis för varje bit på det sätt som fig 1.25 ger exempel på. I fig 1.25 utförs AND- funktion på register A och B. Resultatet placeras i register"R. Enligt |
| [17 / PDF 24](../bookpages/Page_023.jpg) | funktion på register A och B. Resultatet placeras i register"R. Enligt AND-funktionen måste en viss bit innehålla en etta i både A- och B- registret för att motsvarande bit i resultatregistret ska bli ett. |
| [17 / PDF 24](../bookpages/Page_023.jpg) | Vill man nollställa en bit utan att ändra övriga bitar i ett ord kan man använda AND-funktionen på det sätt som visas i fig 1.26a. |
| [17 / PDF 24](../bookpages/Page_023.jpg) | hur de fyra mest signifikanta bitarna ur en byte kan maskas bort med AND-funktionen och masken 00001111. |
| [17 / PDF 24](../bookpages/Page_023.jpg) | gångar (register A och register B), en utgång (register R) samt ett antal styringångar, i vårt exempel INR (för inkrementering), AND, XOR och SH (för skift). |
| [18 / PDF 25](../bookpages/Page_024.jpg) | Mask: ACORERRee AND X-reg: [XIXIXIXIXIXIXIX |
| [18 / PDF 25](../bookpages/Page_024.jpg) | To ee AND L[olololoTxIxIx]Xx X-reg: [XIX[X[Xx[X[X[x]x] |
| [18 / PDF 25](../bookpages/Page_024.jpg) | Fig 1.26 Exempel på bithantering med hjälp av AND, OR och XOR |
| [19 / PDF 26](../bookpages/Page_025.jpg) | b) AND OR XOR |
| [19 / PDF 26](../bookpages/Page_025.jpg) | INR AND -XOR SH |
| [27 / PDF 34](../bookpages/Page_033.jpg) | inkrementering och skift. CMC8 innehåller de logiska funktionerna AND och XOR samt rotation i två varianter. LSI-kretsen har storleken 35 mm? och innehåller ca 4000 transistorer. Den kan matas med |
| [46 / PDF 53](../bookpages/Page_052.jpg) | tioner (mintermer) och därigenom spara ett stort antal bitar. Ett PLA är i princip en AND-OR-krets, fig 4.7. |
| [46 / PDF 53](../bookpages/Page_052.jpg) | I ett antal AND-(eller NAND) kretsar avkodas instruktionerna. Varje instruktion behöver en viss uppsättning MOP:ar och i fig 4.7 har vi |
| [46 / PDF 53](../bookpages/Page_052.jpg) | ritat ut hur MOP:arna ) (&) (0) osv styrs via OR-grindar från LRS- instruktionens AND-grind. |
| [67 / PDF 74](../bookpages/Page_073.jpg) | XRI O0101ARRR /DATA/ FÅ 3 EXCLUSIVE OR IMMEDIATE. ANI O0110RAR /DATA/ Z 3 AND IMMEDIATE. CPY O01118RR 2 COPY REGISTER INTO X-REGISTER. |
| [67 / PDF 74](../bookpages/Page_073.jpg) | DCR 10 100RRR Z 3 DECREMENT REGISTER. XOR 1010 18RRR 2 3 EXCLUSIVE OR OF REGISTER AND X-REGISTER.RESULT TO X REG. |
| [67 / PDF 74](../bookpages/Page_073.jpg) | X-REGISTER.RESULT TO X REG. AND 10110RR8R Zz 3 LOGICAL AND OF REGISTER AND X-REGISTER. RESULT TO X REG. |
| [67 / PDF 74](../bookpages/Page_073.jpg) | X-REGISTER. RESULT TO X REG. EXR 10171718RR 3 EXCHANGE REGISTER AND X-REGISTER. SCW 00001000 £SSS/ 3+ SEND CONTROL SIGNALS AND WAIT. |
| [67 / PDF 74](../bookpages/Page_073.jpg) | EXR 10171718RR 3 EXCHANGE REGISTER AND X-REGISTER. SCW 00001000 £SSS/ 3+ SEND CONTROL SIGNALS AND WAIT. SES 00001001 ZSSSA 3 SEND CONTROL SIGNALS. |
| [75 / PDF 82](../bookpages/Page_081.jpg) | väl logiska som aritmetiska operationer, vilket framgår av fig 5.1. Låt oss undersöka ett exempel, instruktionen AND (dvs "Logical AND of register and X-reg Result to X-reg''). |
| [75 / PDF 82](../bookpages/Page_081.jpg) | Låt oss undersöka ett exempel, instruktionen AND (dvs "Logical AND of register and X-reg Result to X-reg''). |
| [75 / PDF 82](../bookpages/Page_081.jpg) | AND = logisk OCH-funktion |
| [75 / PDF 82](../bookpages/Page_081.jpg) | Vv Fig 5.7 Mikroprogram för fas 1 och 2 hos AND-instruktionen (R(A):R7) a) Funktioner |
| [86 / PDF 93](../bookpages/Page_092.jpg) | Utgången STRCS kan aktiveras av tvåordsinstruktionen SCW (send control signals and wait). Därvid läggs instruktionens andra ord ut på databussen. Detta ord kan användas som kont- |
| [87 / PDF 94](../bookpages/Page_093.jpg) | den träffar på en HALT-instruktion. Då stannar den. CMC8 har ingen HALT-instruktion men instruktionen SCW (send control signal and wait) ger samma effekt, dvs stoppar processorn och lägger den i vänteläge. |
| [94 / PDF 101](../bookpages/Page_100.jpg) | Ö il d (dvs oktala talet 0198) med instruktionen ANI P18 (AND immediate). |
| [95 / PDF 102](../bookpages/Page_101.jpg) | När utportens adress (Pg1) ligger på adressbussen ger avkodaren i ut- porten en utsignal (AE) som grindas (AND) tillsammans med EDE och skrivkommando (WRITE hög). Denna kombination klockar in data från |
| [97 / PDF 104](../bookpages/Page_103.jpg) | SCW send control signals and wait |
| [131 / PDF 138](../bookpages/Page_137.jpg) | Outputs are enabled when valid entry is made and go into TRI-STATE when key is released. |
| [135 / PDF 142](../bookpages/Page_141.jpg) | Efter hoppet hämtar CMCB38 efterföljande instruktion från sida 3 och därför är denna sidadress (PP = 1 och P1 = 1) avkodad i en AND-grind (under D-vippan i fig 7.19). Utsignalen (P M3) från denna grind noll- |
| [158 / PDF 165](../bookpages/Page_164.jpg) | sidan av en glasplåt (negativ). Mönstret exponeras och framkallas, förminskas och repeteras på en ny fotoplåt, ett s k step and repeat- original (master plate). Som mönsterbärare på denna plåt kan andra |
| [158 / PDF 165](../bookpages/Page_164.jpg) | er negativ Step and re- peatoriginal Fotorepeater |
| [159 / PDF 166](../bookpages/Page_165.jpg) | Den tidsödande och dyra delen av tillverkningen (mellannegativ och step and repeat - original) görs normalt bara vid prototyptillverkning och tar någon vecka i anspråk. Arbetsmasktillverkning går snabbt och |
| [186 / PDF 193](../bookpages/Page_192.jpg) | Det manuella förfarandet att skära ut layouten i dubbellagrig plast (cut and strip) med därpå följande fotoreduktion, är på väg att försvin- na pga den stora osäkerheten och tidsåtgången jämfört med automat- |
| [190 / PDF 197](../bookpages/Page_196.jpg) | negativ i 4 eller 10 gångers förstoring, vilka sedan används i den s k step and repeat-kameran för tillverkning av masker i skala 1:1, fig 9.1. Denna kamera styrs av ett enkelt programverk. |
| [215 / PDF 222](../bookpages/Page_221.jpg) | ''New Processes get more out of LSI" "Large and Medium Scale Integration" L Altman et al, Electronics vol 50 nr 17 |
| [215 / PDF 222](../bookpages/Page_221.jpg) | Aug 18 1977 "Comparison of Low Power Schottky TTL and "Digital teknik" |
| [215 / PDF 222](../bookpages/Page_221.jpg) | "Low Threshold Low-Power CMOS/SOS for "Memories score new highs in speed and High-Frequency Counter Applications" |
| [215 / PDF 222](../bookpages/Page_221.jpg) | G Markesjö, Esselte Studium 1976 "The relative performance and merits of "Bli bekant med en minidator' |
| [216 / PDF 223](../bookpages/Page_222.jpg) | "Miecrocomputers - Present and Future" M Dance, Electronics Industry, Juni 1977 |
| [216 / PDF 223](../bookpages/Page_222.jpg) | ""Process and device modeling for IC-design" NOTO Advanced Study Institute, July 1977 |
| [217 / PDF 224](../bookpages/Page_223.jpg) | adresspekare 42 TR fotoresist 157, 159 KIM-1 109 aktiv yta 201 cut and strip 186 framkant 9 kiselskiva 156 alignment mark 160 cykel 31, 60 förstudie 199 kit 109 |
| [218 / PDF 225](../bookpages/Page_224.jpg) | register 10, 37 statusregister 103 vippa 7 offerering 195, 197 registercell 12, 14 step and repeat-original wired or 98 operandadress 31 register indirect 158 wiring list 205 |

## EXR

Patterns: `EXR`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | X-REGISTER. RESULT TO X REG. EXR 10171718RR 3 EXCHANGE REGISTER AND X-REGISTER. SCW 00001000 £SSS/ 3+ SEND CONTROL SIGNALS AND WAIT. |

## SCW

Patterns: `SCW`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | EXR 10171718RR 3 EXCHANGE REGISTER AND X-REGISTER. SCW 00001000 £SSS/ 3+ SEND CONTROL SIGNALS AND WAIT. SES 00001001 ZSSSA 3 SEND CONTROL SIGNALS. |
| [68 / PDF 75](../bookpages/Page_074.jpg) | Instruktionen SCW har format f. Det andra ordet utgör i detta fall styr- signaler (control signals). |
| [86 / PDF 93](../bookpages/Page_092.jpg) | Utgången STRCS kan aktiveras av tvåordsinstruktionen SCW (send control signals and wait). Därvid läggs instruktionens |
| [87 / PDF 94](../bookpages/Page_093.jpg) | den träffar på en HALT-instruktion. Då stannar den. CMC8 har ingen HALT-instruktion men instruktionen SCW (send control signal and wait) ger samma effekt, dvs stoppar processorn och lägger den i vänteläge. |
| [97 / PDF 104](../bookpages/Page_103.jpg) | Fig 6.14 Kontrollfunktionen hos CMC8 med instruktionerna SCW och SCS |
| [97 / PDF 104](../bookpages/Page_103.jpg) | SCW send control signals and wait |
| [97 / PDF 104](../bookpages/Page_103.jpg) | SCW och SCS är tvåordsinstruktioner med format c (fig 5.2 i kap 5). |
| [97 / PDF 104](../bookpages/Page_103.jpg) | När en SCW- eller SCS-instruktion exekveras får man en strobpuls på den speciella strobpulsutgången |
| [97 / PDF 104](../bookpages/Page_103.jpg) | När denna utgång ligger hög innehåller databussen det ord som anges av ord 2 hos SCW- eller SCS-instruktionen. Man kan enkelt lagra det- ta ord i en latch som klockas av STRCS-signalen på det sätt som fram- |
| [98 / PDF 105](../bookpages/Page_104.jpg) | Vill vi ha kvittens på att lampan tänds kan vi använda instruktionen SCW. Den lägger CMC8 i ett vänteläge och detta vänteläge kan hävas med låg signal på SCWR-ingången. Kopplar vi utspänningen från foto- |
| [98 / PDF 105](../bookpages/Page_104.jpg) | Vi ser alltså att CMC8 är speciellt användbar för uppbyggnad av enkel styrlogik tack vare instruktionerna SCS och SCW samt kontrollsignaler- na STRCS (ut) och SCWR (in). |
| [99 / PDF 106](../bookpages/Page_105.jpg) | SCW-instruktionens mikroprogram |
| [99 / PDF 106](../bookpages/Page_105.jpg) | Vi får en utförligare beskrivning av SCW-instruktionen av mikropro- grammet i fig 6.17. Under fas F$ hämtas instruktionen samtidigt som |
| [99 / PDF 106](../bookpages/Page_105.jpg) | Instruktionen (SCW = Opgd1gpg) läggs i instruktionsregistret under T5 och vid T6 läggs programräknaren ut. Programräknaren innehåller nu |
| [99 / PDF 106](../bookpages/Page_105.jpg) | och vid T6 läggs programräknaren ut. Programräknaren innehåller nu adressen till SCW-instruktionens andra ord och det är just det kontroll- ord vi utnyttjat för tändning av lampan i fig 6.15. |
| [100 / PDF 107](../bookpages/Page_106.jpg) | Fig 6.17 Mikroprogram för SCW-instruktionen |
| [100 / PDF 107](../bookpages/Page_106.jpg) | SCW-instruktionens tidsdiagram |
| [100 / PDF 107](../bookpages/Page_106.jpg) | Mikroprogrammet för SCW-instruktionen avspeglas i tidsdiagrammet i fig 6.18. Mikroprogram och tidsdiagram beskriver ju samma för- |
| [144 / PDF 151](../bookpages/Page_150.jpg) | 620 SCW Halt g1g |

## SCS

Patterns: `SC\s*S, SES`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [3 / PDF 10](../bookpages/Page_009.jpg) | \| SES I I \| a) Vss ER 1 b) |
| [9 / PDF 16](../bookpages/Page_015.jpg) | Vid klockpulsens positiva flank stryps T1 och T4 medan T2 och T3 blir ledande. Insignalens värde vid klockpulsens positiva flank låses därmed av mästaren och förs dessutom vidare till slavens utgång Q. |
| [9 / PDF 16](../bookpages/Page_015.jpg) | D-latchen i fig 1.12 är "genomskinlig" vid klockning. Utgången (Q) föl- jer ingången och låses till det invärde som gäller vid klockpulsens bakkant (då T1 spärras och T2 går till). |
| [13 / PDF 20](../bookpages/Page_019.jpg) | Al od I - Em SVT SV Register 1 SES från S [ JE Avkodare |
| [15 / PDF 22](../bookpages/Page_021.jpg) | READ och WRITE-ingångarna hopkopplade till en gemensam R/W-in- gång. När denna kontrollingång ligger hög läses data ut från minnet |
| [22 / PDF 29](../bookpages/Page_028.jpg) | Under fas 2 måste såväl A som BR hålla ett tal på utgången samtidigt som ett nytt läses in på ingången. Både A och BR måste alltså vara uppbyggda av MS-vippor. |
| [49 / PDF 56](../bookpages/Page_055.jpg) | Fig 4.9 Tidsdiagram för instruktionen LRS (LRS = läs från dataminnet) Streckad pil anger när data avläses, dvs krav på "data valid" |
| [50 / PDF 57](../bookpages/Page_056.jpg) | Instruktionen läses in och tolkas under tid T6 i fas d. Samtidigt läggs nästa adress i programminnet ut på AB. Detta är markerat med PC+1 |
| [50 / PDF 57](../bookpages/Page_056.jpg) | sen DB. I fas 1 och fas 2 avläses databussen. Minnet måste här vara färdigt för avläsning efter 3 deltider. Detta är ett hårdare krav på snabbhet |
| [51 / PDF 58](../bookpages/Page_057.jpg) | T5: Databussen läses in till instruktionsregistret. Instruktions- registret ligger öppet för inläsning under hela T5 och det sista |
| [53 / PDF 60](../bookpages/Page_059.jpg) | latch som ligger öppen under T5 och det är alltså värdet vid slutet av T5 som inläses. BR är en MS-vippa som triggas på klockpulsens po- sitiva framkant, dvs vid övergången från T4 till T5. Avläsningen av |
| [55 / PDF 62](../bookpages/Page_061.jpg) | RME SES EN I I |
| [64 / PDF 71](../bookpages/Page_070.jpg) | (PG) nollställs under T$9. Vid T1 nollställs databussen DI. Vid T2 noll- ställs N-registret och vid T4 läses DI in till R(N) = Rf. Efter en maskincykel (dvs 8 deltider) är CMC8 nollställd på det sätt |
| [67 / PDF 74](../bookpages/Page_073.jpg) | SCW 00001000 £SSS/ 3+ SEND CONTROL SIGNALS AND WAIT. SES 00001001 ZSSSA 3 SEND CONTROL SIGNALS. JAR 00001100 /ADR/ 3 JUMP TO SUBROUTINE. |
| [71 / PDF 78](../bookpages/Page_077.jpg) | Vid F2T2 höjs PME för läsning i programminnet. Vi antar nu att ingen WATT-cykel är inlagd och då inläses data (= hoppadressen) från pro- gramminnet vid början av F2T5 (DB— BR). Vid F2T6 flyttas adressen |
| [97 / PDF 104](../bookpages/Page_103.jpg) | Fig 6.14 Kontrollfunktionen hos CMC8 med instruktionerna SCW och SCS |
| [97 / PDF 104](../bookpages/Page_103.jpg) | SCS send control signals |
| [97 / PDF 104](../bookpages/Page_103.jpg) | SCW och SCS är tvåordsinstruktioner med format c (fig 5.2 i kap 5). |
| [97 / PDF 104](../bookpages/Page_103.jpg) | När en SCW- eller SCS-instruktion exekveras får man en strobpuls på den speciella strobpulsutgången |
| [97 / PDF 104](../bookpages/Page_103.jpg) | När denna utgång ligger hög innehåller databussen det ord som anges av ord 2 hos SCW- eller SCS-instruktionen. Man kan enkelt lagra det- ta ord i en latch som klockas av STRCS-signalen på det sätt som fram- |
| [98 / PDF 105](../bookpages/Page_104.jpg) | Behöver vi inte kontrollera att lamporna tänds kan vi använda instruk- tionen SCS. Den lägger ut styrord på databussen och ger strobpuls. Därefter fortsätter CMC8 med nästa instruktion (oavsett vad som hän- |
| [98 / PDF 105](../bookpages/Page_104.jpg) | Vi ser alltså att CMC8 är speciellt användbar för uppbyggnad av enkel styrlogik tack vare instruktionerna SCS och SCW samt kontrollsignaler- na STRCS (ut) och SCWR (in). |
| [124 / PDF 131](../bookpages/Page_130.jpg) | F1T3 Ingen yttre förändring. Enbart arbete i CMC8. Vid början av SSR F1T5 avläses databussen och mellanlagras i BR. |
| [124 / PDF 131](../bookpages/Page_130.jpg) | F2T2 SME går hög och position 125 (oktalt) i dataminnet avläses. Lampan bredvid SM lyser, vilket visar att dataminnet är ad- |
| [129 / PDF 136](../bookpages/Page_135.jpg) | Kör sedan detta program manuellt. Först lyser adressdioden i ED2 och dess värde läses in i CMC8:s register 3. Efter en stund lyser adress- lampan i ED1 och nu kopieras siffrorna från ED2 över till ED1. ED2 |
| [135 / PDF 142](../bookpages/Page_141.jpg) | av lämpliga instruktioner. I den sekvens som följer efter adress 363 finns bl a en SCS-instruktion. När denna exekveras läggs ett kontroll- ord på databussen samtidigt som kontrollutgången STRCS på CMC8 av- |
| [136 / PDF 143](../bookpages/Page_142.jpg) | Med en SCS-instruktion (men med bit f låg) kan D-vippan nollställas under programkontroll och därmed kan CMC8 hoppa ur KEX-program- |
| [150 / PDF 157](../bookpages/Page_156.jpg) | Fig 8.8 visar de olika arbetsmomenten i STARTA KEX-rutinen. Först sätts KEX-vippan med en SCS-instruktion. Därefter ställs ljuset i displayen så att enbart den högra siffran (för programminnet PM) ly- |
| [150 / PDF 157](../bookpages/Page_156.jpg) | g17 SCS Tänd KEX- g11 020 + 201 lampan 261 |
| [151 / PDF 158](../bookpages/Page_157.jpg) | lagring av data eller som modregister. Fig 8.9 ger en sammanställ- ning av hur KEX-programmet disponerar register, adresser och SCS- kommandon. |
| [152 / PDF 159](../bookpages/Page_158.jpg) | R2 Minnesmod (ED6) SC S-kommando R3 AD/DA-mod |
| [152 / PDF 159](../bookpages/Page_158.jpg) | Vanligen skriver man rutiner som inte störs av kontaktstudsar. Exem- pelvis avläses tangentens tillstånd vid två tillfällen med 10 ms tidsmel- lanrum. Om de avlästa värdena är lika antar man att kontaktstudsarna |
| [152 / PDF 159](../bookpages/Page_158.jpg) | När en tangent trycks ned hoppar CMC8 över till den nedre slingan och ligger kvar där tills tangenten släpps. Tangentens kod läses in till CMC8 i den övre slingan (KB—R6) men CMC8 fortsätter inte sitt ar- |

## JSR

Patterns: `JSR, JAR`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [51 / PDF 58](../bookpages/Page_057.jpg) | PC (dvs register $) och PG-registret nollställda. Enligt fig 4.10 bör- jar nu CMC83 sitt arbete på följande sätt: Tf: Det register som adresseras av N (programräknaren) läggs ut |
| [67 / PDF 74](../bookpages/Page_073.jpg) | SES 00001001 ZSSSA 3 SEND CONTROL SIGNALS. JAR 00001100 /ADR/ 3 JUMP TO SUBROUTINE. RSR 00001111 2 RETURN FROM SUBROUTINE. |
| [69 / PDF 76](../bookpages/Page_075.jpg) | CMC8 har ett tiotal hoppinstruktioner. Av dessa är JMP, JCR och JSR ovillkorliga hopp. |
| [70 / PDF 77](../bookpages/Page_076.jpg) | i JCR-instruktionen (som är en enordsinstruktion). Vid JSR, dvs hopp till subrutin, inkrementeras N-registret och därför förstörs inte den gamla adressen. |
| [70 / PDF 77](../bookpages/Page_076.jpg) | ret varigenom mikroprocessorn återgår till sin tidigare programräk- nare med det innehåll den hade efter JSR-instruktionens hämtning, dvs före hoppet. |
| [71 / PDF 78](../bookpages/Page_077.jpg) | Hopp till subrutin (JSR) och återhopp från subrutin (RSR) skiljer sig från övriga ovillkorliga hopp i ett avseende. N-registret inkremente- |
| [71 / PDF 78](../bookpages/Page_077.jpg) | från övriga ovillkorliga hopp i ett avseende. N-registret inkremente- ras och därmed flyttas programräknaren vid första JSR från Rå till RI: |
| [71 / PDF 78](../bookpages/Page_077.jpg) | Fas 1 och 2 för mikroprogrammen för JSR och RSR framgår av fig 5. 4. Vi ser här inkrementeringen av N-registret vid tid F2T2 i JSR-instruk- |
| [71 / PDF 78](../bookpages/Page_077.jpg) | Fas 1 och 2 för mikroprogrammen för JSR och RSR framgår av fig 5. 4. Vi ser här inkrementeringen av N-registret vid tid F2T2 i JSR-instruk- tionen och motsvarande dekrementering vid samma tid i RSR-instruk- |
| [71 / PDF 78](../bookpages/Page_077.jpg) | tionen och motsvarande dekrementering vid samma tid i RSR-instruk- tionen. Observera att JSR tar tre maskincykler medan RSR klarar sig med två, tack vare inkrementeringen av F vid F1T1. |
| [71 / PDF 78](../bookpages/Page_077.jpg) | JSR = hopp till subrutin |
| [71 / PDF 78](../bookpages/Page_077.jpg) | Fig 5.4 Mikroprogram för fas 1 och 2 för subrutininstruktionerna JSR (hopp till subrutin) och RSR (återhopp från subrutin) (Fig 4.10 visar fas Ff) |
| [105 / PDF 112](../bookpages/Page_111.jpg) | Det kan här vara av intresse att jämföra subrutinhopp (JSR), avbrott via INT-ingången och hopp förorsakat av signal på någon av testin- |
| [144 / PDF 151](../bookpages/Page_150.jpg) | f14 JSR 014 g15 /ADR/ Hoppa till pgg dög |
| [146 / PDF 153](../bookpages/Page_152.jpg) | 015 /ED4/ p04 616 JSR S 014 g17 /Vänta 10/ San TE 100 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | (23 /ED4/ 004 p24 JSR 014 025 /Vänta 10/ S 1gg |
| [146 / PDF 153](../bookpages/Page_152.jpg) | 025 /Vänta 10/ S 1gg d26 JSR Vänta 20 g14 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | 033 /ED4/ pp4 034 JSR g14 035 /Vänta 10/ 168 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | 035 /Vänta 10/ 168 036 JSR 3 014 p37 vanta 10/ Nar on 160 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | p37 vanta 10/ Nar on 160 046 JSR g14 g41 /Vänta 10/ 1gg |
| [146 / PDF 153](../bookpages/Page_152.jpg) | f45 /ED4/ 004 g46 JSR $14 f47 /Vänta 10/ E 10p |
| [146 / PDF 153](../bookpages/Page_152.jpg) | f47 /Vänta 10/ E 10p $56 JSR Vänta 20 g14 |
| [146 / PDF 153](../bookpages/Page_152.jpg) | $55 /ED4/ P4 056 JSR z g14 Ö57 fvänta 10 j GERE Te 108 |
| [148 / PDF 155](../bookpages/Page_154.jpg) | grammet (adress 113 och framåt). Etiketten antyder att det är fråga om en lång vänterutin. För att slippa upprepa "JSR Vänta 10' tjugo- sju gånger (vilket tar stor plats i programminnet) kan vi exempelvis |
| [148 / PDF 155](../bookpages/Page_154.jpg) | 114 = 033 p33 LOOP 115 JSR g14 116 /Vänta 10/ 1009 |
| [148 / PDF 155](../bookpages/Page_154.jpg) | Vi har här laddat register 6 med 27 (oktalt 233) och lagt "JSR Vänta 10" i en slinga (LOOP) som vi kör runt 27 gånger. Det dröjer därför 270 s |

## RSR

Patterns: `RSR`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [62 / PDF 69](../bookpages/Page_068.jpg) | under fas F$ av efterföljande instruktion. Detta framgår av fig 4.19 (den efterföljande instruktionen i fig 4.19 är RSR, return from subroutine). |
| [63 / PDF 70](../bookpages/Page_069.jpg) | (dvs 002) ligger i den nya programräknaren. Programmet för avbrottsrutinen måste avslutas med instruktionen RSR (return from subroutine) vilken medför att N dekrementeras (N-1— N) |
| [64 / PDF 71](../bookpages/Page_070.jpg) | punkter) och vars mikroprogram framgår av fig 4.20b. Här nollställs INTE-vippan under T/ och förblir i detta läge tills efterföljande RSR- instruktion åter ettställer den (fig 4.19). |
| [64 / PDF 71](../bookpages/Page_070.jpg) | Efterföljande instruktion (RSR) |
| [64 / PDF 71](../bookpages/Page_070.jpg) | Fig 4.19 EIN-instruktionen ettställer INTE-vippan först i hämtnings- fasen till efterföljande instruktion (i detta exempel RSR) |
| [67 / PDF 74](../bookpages/Page_073.jpg) | JAR 00001100 /ADR/ 3 JUMP TO SUBROUTINE. RSR 00001111 2 RETURN FROM SUBROUTINE. NOP 00000000 1 NO OPERATION. |
| [70 / PDF 77](../bookpages/Page_076.jpg) | förstörs inte den gamla adressen. Vid återhopp (RSR = return from subroutine) dekrementeras N-regist- ret varigenom mikroprocessorn återgår till sin tidigare programräk- |
| [71 / PDF 78](../bookpages/Page_077.jpg) | Hopp till subrutin (JSR) och återhopp från subrutin (RSR) skiljer sig från övriga ovillkorliga hopp i ett avseende. N-registret inkremente- |
| [71 / PDF 78](../bookpages/Page_077.jpg) | Fas 1 och 2 för mikroprogrammen för JSR och RSR framgår av fig 5. 4. Vi ser här inkrementeringen av N-registret vid tid F2T2 i JSR-instruk- |
| [71 / PDF 78](../bookpages/Page_077.jpg) | Vi ser här inkrementeringen av N-registret vid tid F2T2 i JSR-instruk- tionen och motsvarande dekrementering vid samma tid i RSR-instruk- tionen. Observera att JSR tar tre maskincykler medan RSR klarar sig |
| [71 / PDF 78](../bookpages/Page_077.jpg) | tionen och motsvarande dekrementering vid samma tid i RSR-instruk- tionen. Observera att JSR tar tre maskincykler medan RSR klarar sig med två, tack vare inkrementeringen av F vid F1T1. |
| [71 / PDF 78](../bookpages/Page_077.jpg) | RSR = återhopp från subrutin Tf( TT T2 TE T4 TT T6 7 |
| [71 / PDF 78](../bookpages/Page_077.jpg) | Fig 5.4 Mikroprogram för fas 1 och 2 för subrutininstruktionerna JSR (hopp till subrutin) och RSR (återhopp från subrutin) (Fig 4.10 visar fas Ff) |
| [143 / PDF 150](../bookpages/Page_149.jpg) | 11 /ADR/ gp4 DC, 4 12 RSR 2 g17 |
| [147 / PDF 154](../bookpages/Page_153.jpg) | 117 /HOPP/ 104 112 RSR g17 |
| [153 / PDF 160](../bookpages/Page_159.jpg) | Ja 15 nod RI/ g16 \| 816 RSR $17 - (Tangent |

## NOP

Patterns: `NOP`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | RSR 00001111 2 RETURN FROM SUBROUTINE. NOP 00000000 1 NO OPERATION. EIN 00000011 IT 1 ENABLE INTERRUPT |
| [73 / PDF 80](../bookpages/Page_079.jpg) | Om hoppvillkoret inte uppfylls vilar processorn (NOP = no operation) och MOP 2) i fig 5.5 förblir låg. |
| [73 / PDF 80](../bookpages/Page_079.jpg) | H = f: Ö—F NOP |
| [147 / PDF 154](../bookpages/Page_153.jpg) | Ö72 Ljustyp 4 301 Ö73 NOP pg Ö74 NOP Reserverad 000 |
| [147 / PDF 154](../bookpages/Page_153.jpg) | Ö73 NOP pg Ö74 NOP Reserverad 000 075 NOP plats för 60 |
| [147 / PDF 154](../bookpages/Page_153.jpg) | Ö74 NOP Reserverad 000 075 NOP plats för 60 $76 NOP framtida 060 |
| [147 / PDF 154](../bookpages/Page_153.jpg) | 075 NOP plats för 60 $76 NOP framtida 060 Ö77 NOP ljustyper 000 |
| [147 / PDF 154](../bookpages/Page_153.jpg) | $76 NOP framtida 060 Ö77 NOP ljustyper 000 Vänta 10 1gf TRA S g43 |

## EIN

Patterns: `EIN`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [62 / PDF 69](../bookpages/Page_068.jpg) | När man sedan åter vill göra CMC8 mottaglig för avbrott ettställer man INTE-vippan med instruktionen EIN (enable interrupt). Ettställ- ningen av INTE-vippan exekveras därvid först vid början av deltid T2 |
| [64 / PDF 71](../bookpages/Page_070.jpg) | EIN |
| [64 / PDF 71](../bookpages/Page_070.jpg) | Fig 4.19 EIN-instruktionen ettställer INTE-vippan först i hämtnings- fasen till efterföljande instruktion (i detta exempel RSR) |
| [67 / PDF 74](../bookpages/Page_073.jpg) | NOP 00000000 1 NO OPERATION. EIN 00000011 IT 1 ENABLE INTERRUPT DIN 00000010 i 1 DISABLE INTERRUPT |

## DIN

Patterns: `DIN`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [62 / PDF 69](../bookpages/Page_068.jpg) | terrupt enable). Denna vippa (eller flagga) sätts av programmet. Ge- nom att nollställa INTE-vippan (med enords-instruktionen DIN, disable interrupt) kan man förhindra avbrott under exekveringen av känsliga |
| [67 / PDF 74](../bookpages/Page_073.jpg) | EIN 00000011 IT 1 ENABLE INTERRUPT DIN 00000010 i 1 DISABLE INTERRUPT SEL 00000101 = 1 SET LINK FLIP FLOP |
| [114 / PDF 121](../bookpages/Page_120.jpg) | den 64-poliga kontakten längst uppe till höger. Kontakten är av typ DIN 41612 och har de funktioner som framgår av fig 7.6. |

## SEL

Patterns: `SEL`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | DIN 00000010 i 1 DISABLE INTERRUPT SEL 00000101 = 1 SET LINK FLIP FLOP REL 00000100 C 1 RESET LINK FLIP FLUP |
| [75 / PDF 82](../bookpages/Page_081.jpg) | Till skillnad från 8080 har CMC8 entydiga instruktioner som bara har till uppgift att ställa eller nollställa flaggorna (SEZ, REZ, SEL och REL). L-flaggan används enbart vid skift och rotation, och vi återkom- |
| [107 / PDF 114](../bookpages/Page_113.jpg) | signalen på en av testingångarna kan man läsa in seriedata till ett re- gister. Linkvippan styrs med instruktionerna SEL och REL (fig 5. 1). |
| [108 / PDF 115](../bookpages/Page_114.jpg) | FEST —P ----SEL eller SVE \| |

## REL

Patterns: `REL`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [31 / PDF 38](../bookpages/Page_037.jpg) | Observera att LRS tog 3 faser eller 3 cykler i anspråk. Det finns in- struktioner (exempelvis REL, nollställ linkvippan) som exekveras di- rekt och som därför endast tar en cykel i anspråk. Det finns också |
| [67 / PDF 74](../bookpages/Page_073.jpg) | SEL 00000101 = 1 SET LINK FLIP FLOP REL 00000100 C 1 RESET LINK FLIP FLUP SEZ 00000111 Zz 1 SET ZERU FLIP FLUP |
| [75 / PDF 82](../bookpages/Page_081.jpg) | till uppgift att ställa eller nollställa flaggorna (SEZ, REZ, SEL och REL). L-flaggan används enbart vid skift och rotation, och vi återkom- mer snart till detta. Z-flaggan (nollflaggan) påverkas däremot av så- |
| [93 / PDF 100](../bookpages/Page_099.jpg) | vi kopplat in basen på en transistor (ev med seriemotstånd). När bit 2 är hög bottnar (dvs leder) transistorn och relät i dess kollektorkrets drar och tänder lampan. |
| [94 / PDF 101](../bookpages/Page_100.jpg) | 7 Relä 7 1 IN |
| [107 / PDF 114](../bookpages/Page_113.jpg) | signalen på en av testingångarna kan man läsa in seriedata till ett re- gister. Linkvippan styrs med instruktionerna SEL och REL (fig 5. 1). |

## SEZ

Patterns: `SEZ`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | REL 00000100 C 1 RESET LINK FLIP FLUP SEZ 00000111 Zz 1 SET ZERU FLIP FLUP REZ 00000110 Z Å RESET ZERO FLIP FLOP |
| [68 / PDF 75](../bookpages/Page_074.jpg) | Instruktioner som ställer flaggor, exempelvis SEZ (sätt nollflaggan) har detta format. Observera att likartade instruktioner har likartade |
| [69 / PDF 76](../bookpages/Page_075.jpg) | i anspråk för exekvering. Olika instruktioner har olika lång exekverings- tid. Vissa enordsinstruktioner, exempelvis SEZ, exekveras direkt och upptar därför enbart en cykel (dvs 8 deltider). Vissa tvåordsinstruk- |
| [75 / PDF 82](../bookpages/Page_081.jpg) | Till skillnad från 8080 har CMC8 entydiga instruktioner som bara har till uppgift att ställa eller nollställa flaggorna (SEZ, REZ, SEL och REL). L-flaggan används enbart vid skift och rotation, och vi återkom- |

## REZ

Patterns: `REZ`. A pattern alias is a search heuristic, not a claimed alternative mnemonic.

| Printed page candidate / PDF | OCR context |
| --- | --- |
| [67 / PDF 74](../bookpages/Page_073.jpg) | SEZ 00000111 Zz 1 SET ZERU FLIP FLUP REZ 00000110 Z Å RESET ZERO FLIP FLOP |
| [75 / PDF 82](../bookpages/Page_081.jpg) | Till skillnad från 8080 har CMC8 entydiga instruktioner som bara har till uppgift att ställa eller nollställa flaggorna (SEZ, REZ, SEL och REL). L-flaggan används enbart vid skift och rotation, och vi återkom- |

