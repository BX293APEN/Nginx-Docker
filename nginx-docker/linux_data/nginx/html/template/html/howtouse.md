## SQL文法一覧

| 項目             | SQL例                                                                                  | 説明                   |
| -------------- | ------------------------------------------------------------------------------------- | -------------------- |
| データベース作成       | `CREATE DATABASE {selectdb};`                                                         | 新しいデータベースを作成する       |
| テーブル作成         | `CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100), age INT);` | テーブルを作成する            |
| データ追加          | `INSERT INTO users (name, age) VALUES ('Taro', 25);`                                  | レコードを追加する            |
| データ取得          | `SELECT * FROM users;`                                                                | すべてのデータを取得する         |
| 列を指定した取得       | `SELECT name, age FROM users;`                                                        | 指定した列のみ取得する          |
| 条件付き取得         | `SELECT * FROM users WHERE age >= 20;`                                                | 条件に一致するデータを取得する      |
| 複合条件（AND/OR）   | `SELECT * FROM users WHERE age >= 20 AND name = 'Taro';`                              | 複数の条件を組み合わせて取得する     |
| 範囲指定（BETWEEN）  | `SELECT * FROM users WHERE age BETWEEN 20 AND 30;`                                    | 指定範囲内のデータを取得する       |
| 候補指定（IN）       | `SELECT * FROM users WHERE age IN (20, 25, 30);`                                      | 指定した値のいずれかに一致するデータを取得する |
| 曖昧検索（LIKE）   | `SELECT * FROM users WHERE name LIKE 'Ta%';`                                          | 部分一致でデータを検索する（`%`は任意の文字列） |
| NULL判定         | `SELECT * FROM users WHERE age IS NULL;`                                              | 値がNULLのデータを取得する      |
| 重複除外（DISTINCT） | `SELECT DISTINCT age FROM users;`                                                     | 重複を除いた値を取得する         |
| 件数制限（LIMIT）    | `SELECT * FROM users LIMIT 5;`                                                        | 取得件数の上限を指定する         |
| データ更新          | `UPDATE users SET age = 26 WHERE id = 1;`                                             | レコードを更新する            |
| データ削除          | `DELETE FROM users WHERE id = 1;`                                                     | レコードを削除する            |
| テーブル構造確認       | `DESCRIBE users;`                                                                     | テーブルのカラム情報を表示する      |
| テーブル一覧表示       | `SHOW TABLES;`                                                                        | データベース内のテーブル一覧を表示する  |
| データベース一覧表示     | `SHOW DATABASES;`                                                                     | 利用可能なデータベース一覧を表示する   |
| カラム追加（ALTER）   | `ALTER TABLE users ADD COLUMN email VARCHAR(255);`                                    | 既存テーブルに列を追加する        |
| カラム削除（ALTER）   | `ALTER TABLE users DROP COLUMN email;`                                                | 既存テーブルの列を削除する        |
| インデックス作成       | `CREATE INDEX idx_name ON users (name);`                                              | 検索を高速化するインデックスを作成する  |
| テーブル削除         | `DROP TABLE users;`                                                                   | テーブルを削除する            |
| データベース削除       | `DROP DATABASE {selectdb};`                                                           | データベースを削除する          |
| 並び替え           | `SELECT * FROM users ORDER BY age DESC;`                                              | 指定した列で並び替える          |
| 件数取得           | `SELECT COUNT(*) FROM users;`                                                         | レコード数を取得する           |
| グループ化          | `SELECT age, COUNT(*) FROM users GROUP BY age;`                                       | 同じ値ごとに集計する           |
| グループ絞り込み（HAVING） | `SELECT age, COUNT(*) FROM users GROUP BY age HAVING COUNT(*) > 1;`               | 集計結果に対して条件で絞り込む      |
| 別名指定（AS）      | `SELECT name AS user_name FROM users;`                                                | 列や式に別名を付ける           |
| 文字列結合（CONCAT）  | `SELECT CONCAT(name, 'さん') FROM users;`                                              | 文字列を連結する             |
| 結合（INNER JOIN） | `SELECT u.name, o.product FROM users u INNER JOIN orders o ON u.id = o.user_id;`      | 両テーブルに存在する行のみを結合して取得する |
| 結合（LEFT JOIN）  | `SELECT u.name, o.product FROM users u LEFT JOIN orders o ON u.id = o.user_id;`       | 左側テーブルの全行と、一致する右側テーブルの行を取得する |
| サブクエリ          | `SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);`                       | SQL文の中に別のSQL文を組み込む   |
| トランザクション開始     | `START TRANSACTION;`                                                                  | 一連の処理をまとめて実行する準備をする  |
| トランザクション確定     | `COMMIT;`                                                                             | トランザクション内の変更を確定する    |
| トランザクション取消     | `ROLLBACK;`                                                                           | トランザクション内の変更を取り消す    |

## データベースの選択について

画面上部の**プルダウンメニュー**から使用したいデータベースを選択
→ `USE データベース名;`は不要

## 補足

- 文字列や日付は `'` (シングルクォート) 又は `"` (ダブルクォート) で囲む。
- 予約語やスペースを含む識別子は`` ` ``（バッククォート）で囲む。
- 1行コメントは`-- `（ハイフン2つ＋半角スペース）、複数行コメントは`/* ... */`で記述する。
