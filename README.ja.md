# CKD Cohort Lab

[English](README.md) · [Tiếng Việt](README.vi.md) · **日本語** · [中文](README.zh.md) · [Français](README.fr.md)

**解析の前に腎臓データを確認し、検査室での尿アルブミン検査が本当に必要な患者を見極めます。**

CKD Cohort Lab は、論文原稿 *“One value or a distribution? Routine urine dipsticks to target albuminuria testing for kidney failure risk”*（投稿中）に付随するブラウザツールとPythonスクリプトです。研究対象は、ベトナム・ホーチミン市のLanh Binh Thang General Hospitalに通院する慢性腎臓病（CKD）G3–G5の外来患者129人です。

- **オンラインツール：** https://ckdco.netlify.app/?lang=ja
- **ソースコード：** https://github.com/lamkienthanh92/ckdcohortlab
- **アーカイブと引用：** https://doi.org/10.5281/zenodo.24189503（バージョン1.2.0。Zenodoのページに全バージョンが表示されます）

> 研究・教育用のツールであり、医療機器ではありません。腎不全リスク式（KFRE）はベトナム人患者では検証されていません。

## ツールの機能

画面は英語、ベトナム語、日本語、中国語、フランス語の5言語に対応しています。上部のバーで言語を選ぶか、アドレスに `?lang=en`、`vi`、`ja`、`zh`、`fr` を付けてください。既定は英語で、選択はブラウザに記憶されます。

1. **データの読み込み：** Excel（.xlsx、.xls、.ods）またはCSVファイル、1行に1人。2つ目のファイル（例：尿定性検査の結果）を患者IDで結合できます。一般的な列名（英語）は自動で対応付けられ、手動でも変更できます。「Unit <列名>」（例：「Unit PRO」）という単位列は行ごとに読み取ります。
2. **分布の確認：** 計算前にすべての列を要約します。完全性、分布、Excelで日付として保存された値、範囲外の値、重複ID、入力ACRとアルブミン÷クレアチニンの比較、入力eGFRとCKD-EPI 2021の比較。整形済みデータをCSVでダウンロードできます。
3. **結果：** KFRE（4変数、北米以外の較正）、KDIGO 2024分類、尿試験紙のACRに対する精度（全体および装置別）、そして分布に基づくトリアージ：
   - KFREの予測区間全体が閾値の片側にある場合に限り、検査室ACRを省略（5年 ≥3% と >5%、2年 >10% と >40%）；
   - 試験紙を単一のACR値に換算する方法との比較；
   - 80/90/95/99%区間の選択、装置項の有無；
   - ランダム70/30分割と装置間での検証；
   - 価格を編集できる直接検査費；
   - 5年KFREの集団レベルと個人レベルの一致；
   - 99%区間を外れた尿アルブミン（検体の同一性の再確認用）。

**プライバシー：** ファイルはブラウザ内でのみ読み込まれます。サーバーへのアップロードや保存は行われず、ページを閉じると消去されます。読み込む前に氏名などの識別情報を削除してください。

`examples/example_synthetic.csv`（合成データ140人、実在の患者ではありません）で試せます。

## 論文の解析の再現

```bash
cd analysis
pip install -r requirements.txt
python triage_analysis.py --data ../examples/example_synthetic.csv --out results
python make_figures.py   --data ../examples/example_synthetic.csv --out figures
```

研究データでは、報告した数値がそのまま再現されます（例：90%区間で129人中66人が検査室ACRを要し、誤判定は2人、単一値換算では25人）。研究データは含まれていません（「データ」を参照）。入力形式とオプションは `analysis/README.md`（英語）に記載しています。

## 方法の概要

log ACRを、年齢・性別・eGFR・糖尿病（臨床モデル）、さらに試験紙蛋白の段階・比重・装置（試験紙モデル）から、最小二乗法とleave-one-out交差検証で予測します。予測区間は 予測値 ± z·s·√(1 + x′(X′X)⁻¹x) です。KFREはACRとともに増加するため、区間の両端でKFREを計算し、両端が閾値の同じ側にある場合に限り検査室ACRなしで判定します。

## リポジトリ構成

| パス | 内容 |
|---|---|
| `index.html` | ブラウザツール（単一ファイル、ビルド不要） |
| `vendor/` | React 18.3.1 と SheetJS 0.18.5（外部のスクリプトホストに依存しないよう同梱） |
| `examples/` | 合成サンプルデータと生成スクリプト |
| `analysis/` | 論文の表と図を再現するPythonスクリプト |
| `netlify.toml` | Netlifyの設定（静的サイト、ビルドなし） |
| `CITATION.cff`、`.zenodo.json` | GitHubとZenodo用の引用メタデータ |

## データ

患者データは含まれていません。匿名化した研究データは、Lanh Binh Thang General Hospitalの倫理審査委員会の承認を条件に、責任著者への合理的な依頼に応じて提供します。

## 引用

> Nguyen ATT, Pham TA, Phan HD, Phan TC, Lam TH, Huynh NH, Tran HNT, Lam TK, Le CV. CKD Cohort Lab: browser tool and analysis code for distribution-based albuminuria triage (version 1.3.0). Zenodo; 2026. https://doi.org/10.5281/zenodo.24189503

## ライセンス

コード：MIT（`LICENSE`を参照）。第三者のコンポーネントはそれぞれのライセンスに従います（`ATTRIBUTION.md`を参照）。
