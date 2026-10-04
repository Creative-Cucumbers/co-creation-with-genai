# co-creation-with-genai

## [2024](./2024/readme.md)

## [2025](./2025/readme.md)

## [2026](./2026/readme.md)

## スライド・授業資料の公開

[授業資料トップ（GitHub Pages）](https://creative-cucumbers.github.io/co-creation-with-genai/)

トップから2026・2025年度の授業スライドを開けます。スライドがない授業は「資料のみ」と表示し、授業資料（GitHub）へのリンクを掲載しています。

### 公開方法

- リポジトリの Settings → Pages → Build and deployment → Source を **GitHub Actions** に設定します。
- `main` にトップページ・対象年度の資料・公開ワークフローの変更をpushすると、`.github/workflows/pages.yml` が公開します。Actionsから手動実行もできます。
- 画像などの相対パスを保つため、2025・2026年度のディレクトリと共通の `images/` をそのまま公開します。

### スライドを追加するとき

`index.html` の該当授業に実在するスライドHTMLへの相対リンクを追加し、「資料のみ」の表示を置き換えます。ゲーム・ポートフォリオなどの実習成果物をスライドと取り違えないようにしてください。講義の順序・名称は各年度の `readme.md` と揃えます。
