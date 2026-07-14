| 項目             | SQL例                                                                                  | 説明                   |
| -------------- | ------------------------------------------------------------------------------------- | -------------------- |
| データベース作成       | `CREATE DATABASE sample_db;`                                                          | 新しいデータベースを作成する       |
| データベース選択       | `USE sample_db;`                                                                      | 使用するデータベースを選択する      |
| テーブル作成         | `CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100), age INT);` | テーブルを作成する            |
| データ追加          | `INSERT INTO users (name, age) VALUES ('Taro', 25);`                                  | レコードを追加する            |
| データ取得          | `SELECT * FROM users;`                                                                | すべてのデータを取得する         |
| 条件付き取得         | `SELECT * FROM users WHERE age >= 20;`                                                | 条件に一致するデータを取得する      |
| データ更新          | `UPDATE users SET age = 26 WHERE id = 1;`                                             | レコードを更新する            |
| データ削除          | `DELETE FROM users WHERE id = 1;`                                                     | レコードを削除する            |
| テーブル構造確認       | `DESCRIBE users;`                                                                     | テーブルのカラム情報を表示する      |
| テーブル一覧表示       | `SHOW TABLES;`                                                                        | データベース内のテーブル一覧を表示する  |
| データベース一覧表示     | `SHOW DATABASES;`                                                                     | 利用可能なデータベース一覧を表示する   |
| テーブル削除         | `DROP TABLE users;`                                                                   | テーブルを削除する            |
| データベース削除       | `DROP DATABASE sample_db;`                                                            | データベースを削除する          |
| 並び替え           | `SELECT * FROM users ORDER BY age DESC;`                                              | 指定した列で並び替える          |
| 件数取得           | `SELECT COUNT(*) FROM users;`                                                         | レコード数を取得する           |
| グループ化          | `SELECT age, COUNT(*) FROM users GROUP BY age;`                                       | 同じ値ごとに集計する           |
| 結合（INNER JOIN） | `SELECT u.name, o.product FROM users u INNER JOIN orders o ON u.id = o.user_id;`      | 複数テーブルを結合して取得する      |