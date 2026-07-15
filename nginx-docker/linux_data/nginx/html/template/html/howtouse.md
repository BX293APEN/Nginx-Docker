## SQL文法一覧

### データベース操作

| SQL | 説明 | 例文 |
| --- | --- | --- |
| CREATE DATABASE | 新しいデータベースを作成する | `CREATE DATABASE {selectdb};` |
| DROP DATABASE | データベースを削除する | `DROP DATABASE {selectdb};` |
| SHOW DATABASES | 利用可能なデータベース一覧を表示する | `SHOW DATABASES;` |

#### データベースの選択について

画面上部の**プルダウンメニュー**から使用したいデータベースを選択  
→ このアプリでは`USE データベース名;`は不要

### テーブル操作

| SQL | 説明 | 例文 |
| --- | --- | --- |
| CREATE TABLE | テーブルを作成する | `CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100), age INT);` |
| DROP TABLE | テーブルを削除する | `DROP TABLE users;` |
| DESCRIBE | テーブルのカラム情報を表示する | `DESCRIBE users;` |
| SHOW TABLES | データベース内のテーブル一覧を表示する | `SHOW TABLES;` |
| CREATE INDEX | 検索を高速化するインデックスを作成する | `CREATE INDEX idx_name ON users (name);` |
| ALTER TABLE ADD COLUMN | 既存テーブルに列を追加する | `ALTER TABLE users ADD COLUMN email VARCHAR(255);` |
| ALTER TABLE DROP COLUMN | 既存テーブルの列を削除する | `ALTER TABLE users DROP COLUMN email;` |
| ALTER TABLE MODIFY COLUMN | 既存の列のデータ型・定義のみを変更する(列名は変更されない) | `ALTER TABLE users MODIFY COLUMN age SMALLINT;` |
| ALTER TABLE CHANGE COLUMN | 列名とデータ型をまとめて変更する | `ALTER TABLE users CHANGE COLUMN age user_age INT;` |

### データ操作(追加・更新・削除)

| SQL | 説明 | 例文 |
| --- | --- | --- |
| INSERT INTO | レコードを追加する | `INSERT INTO users (name, age) VALUES ('Taro', 25);` |
| INSERT INTO(複数行) | 複数のレコードを一度に追加する | `INSERT INTO users (name, age) VALUES ('Taro', 25), ('Hanako', 22);` |
| UPDATE | レコードを更新する | `UPDATE users SET age = 26 WHERE id = 1;` |
| DELETE | レコードを削除する | `DELETE FROM users WHERE id = 1;` |

### データ取得・検索条件

| SQL | 説明 | 例文 |
| --- | --- | --- |
| SELECT 値 | 値を表示する | `SELECT 25;` |
| SELECT * | すべてのデータを取得する | `SELECT * FROM users;` |
| SELECT 列指定 | 指定した列のみ取得する | `SELECT name, age FROM users;` |
| WHERE | 条件に一致するデータを取得する | `SELECT * FROM users WHERE age >= 20;` |
| AND / OR | 複数の条件を組み合わせて取得する | `SELECT * FROM users WHERE age >= 20 AND name = 'Taro';` |
| BETWEEN | 指定範囲内のデータを取得する | `SELECT * FROM users WHERE age BETWEEN 20 AND 30;` |
| IN | 指定した値のいずれかに一致するデータを取得する | `SELECT * FROM users WHERE age IN (20, 25, 30);` |
| LIKE | 部分一致でデータを検索する(`%`は任意の文字列、`_`は任意の1文字) | `SELECT * FROM users WHERE name LIKE 'Ta%';` |
| NOT LIKE | LIKE条件に一致しないデータを取得する | `SELECT * FROM users WHERE name NOT LIKE 'Ta%';` |
| IS NULL | 値がNULLのデータを取得する | `SELECT * FROM users WHERE age IS NULL;` |
| IS NOT NULL | 値がNULLではないデータを取得する | `SELECT * FROM users WHERE age IS NOT NULL;` |
| DISTINCT | 重複を除いた値を取得する | `SELECT DISTINCT age FROM users;` |
| LIMIT | 取得件数の上限を指定する | `SELECT * FROM users LIMIT 5;` |
| COUNT | レコード数を取得する | `SELECT COUNT(*) FROM users;` |
| GROUP BY | 同じ値ごとに集計する | `SELECT age, COUNT(*) FROM users GROUP BY age;` |
| HAVING | 集計結果(GROUP BYの結果)に対して条件で絞り込む | `SELECT age, COUNT(*) FROM users GROUP BY age HAVING COUNT(*) > 1;` |
| AS | 列や式に別名を付ける | `SELECT name AS user_name FROM users;` |
| CONCAT | 文字列を連結する | `SELECT CONCAT(name, 'さん') FROM users;` |
| INNER JOIN | 両テーブルに存在する行のみを結合して取得する | `SELECT u.name, o.product FROM users u INNER JOIN orders o ON u.id = o.user_id;` |
| LEFT JOIN | 左側テーブルの全行と、一致する右側テーブルの行を取得する | `SELECT u.name, o.product FROM users u LEFT JOIN orders o ON u.id = o.user_id;` |
| ( サブクエリ ) | SQL文の中に別のSQL文を組み込む | `SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);` <br> `SELECT (SELECT age FROM users WHERE name = 'Taro') + (SELECT age FROM users WHERE name = 'Hanako');` |
| ORDER BY ASC | 指定した列を昇順に並び替える(省略時のデフォルトもASC) | `SELECT * FROM users ORDER BY name ASC;` |
| ORDER BY DESC | 指定した列を降順に並び替える | `SELECT * FROM users ORDER BY age DESC;` |

#### 昇順・降順について

| 並び順 | SQL |
| --- | --- |
| 昇順(デフォルト) | ASC |
| 降順 | DESC |

- 数値型・日付型の列は**値の大小**で並び替え
- 文字列型の列は**文字コード順 (辞書順)**で並び替え (ASCII文字以外の場合は使用している文字コード・照合順序によって並び順が変わる)
- 複数列を指定すると、先に書いた列を優先して並び替え、同じ値の場合に次の列で並び替える (例 : `ORDER BY age DESC, name ASC`)

#### 演算子・条件式

| SQL | 説明 | 例文 |
| --- | --- | --- |
| = | 値が等しいかどうかを判定する | `SELECT * FROM users WHERE age = 25;` |
| != 又は <> | 値が等しくないかどうかを判定する | `SELECT * FROM users WHERE age != 25;` |
| > | より大きいかどうかを判定する | `SELECT * FROM users WHERE age > 20;` |
| >= | 以上かどうかを判定する | `SELECT * FROM users WHERE age >= 20;` |
| < | より小さいかどうかを判定する | `SELECT * FROM users WHERE age < 20;` |
| <= | 以下かどうかを判定する | `SELECT * FROM users WHERE age <= 20;` |
| + - * / | 四則演算を行う | `SELECT age + 1 FROM users;` |
| % 又は MOD() | 剰余(あまり)を求める | `SELECT age % 2 FROM users;` |
| NOT | 条件式の真偽を反転する | `SELECT * FROM users WHERE NOT age = 20;` |
| CASE WHEN | 条件によって返す値を分岐させる | `SELECT name, CASE WHEN age >= 20 THEN '成人' ELSE '未成年' END AS category FROM users;` |
| IF() | 条件がTRUEかFALSEかで返す値を切り替える | `SELECT IF(age >= 20, '成人', '未成年') FROM users;` |
| IFNULL() | 値がNULLの場合に代わりの値を返す | `SELECT IFNULL(age, 0) FROM users;` |
| COALESCE() | 複数の値のうち最初にNULLでない値を返す | `SELECT COALESCE(nickname, name, '不明') FROM users;` |
| EXISTS | サブクエリの結果が1件でも存在するかを判定する | `SELECT * FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);` |

#### 正規表現

MySQLでは`REGEXP`(別名`RLIKE`)演算子や`REGEXP_LIKE()`などの関数でパターンマッチによる検索・置換ができる。デフォルトでは大文字小文字を区別しない。

| SQL | 説明 | 例文 |
| --- | --- | --- |
| REGEXP | 正規表現でパターンに一致するデータを取得する | `SELECT * FROM users WHERE name REGEXP '^Ta';` |
| NOT REGEXP | 正規表現でパターンに一致しないデータを取得する | `SELECT * FROM users WHERE name NOT REGEXP '^Ta';` |
| RLIKE | `REGEXP`と同じ(別名) | `SELECT * FROM users WHERE name RLIKE 'ro$';` |
| REGEXP_LIKE() | 正規表現の一致を真偽値で判定する関数(WHERE句以外でも使用可) | `SELECT *, REGEXP_LIKE(name, '^[A-Z]') AS is_capitalized FROM users;` |
| REGEXP_REPLACE() | 正規表現に一致した部分を置換する | `SELECT REGEXP_REPLACE(name, '[aeiou]', '*') FROM users;` |
| REGEXP_SUBSTR() | 正規表現に一致した部分文字列を抽出する | `SELECT REGEXP_SUBSTR(name, '[A-Z][a-z]+') FROM users;` |
| REGEXP_INSTR() | 正規表現に一致した部分の位置を取得する | `SELECT REGEXP_INSTR(name, '[0-9]') FROM users;` |

**よく使う正規表現のメタ文字**

| 記号 | 意味 | 例 |
| --- | --- | --- |
| `^` | 文字列の先頭 | `'^Ta'` → 先頭が`Ta` |
| `$` | 文字列の末尾 | `'ro$'` → 末尾が`ro` |
| `.` | 任意の1文字 | `'a.c'` → `abc`, `axc` など |
| `*` | 直前の文字の0回以上の繰り返し | `'ab*'` → `a`, `ab`, `abb` など |
| `+` | 直前の文字の1回以上の繰り返し | `'ab+'` → `ab`, `abb` など(`a`は不一致) |
| `?` | 直前の文字の0回または1回 | `'ab?'` → `a`, `ab` |
| `[abc]` | 角括弧内のいずれか1文字 | `'[Tt]aro'` → `Taro`, `taro` |
| `[^abc]` | 角括弧内以外の1文字 | `'[^0-9]'` → 数字以外の1文字 |
| `[a-z]` | 範囲指定(a〜zのいずれか1文字) | `'^[a-z]'` → 先頭が小文字 |
| `{{n,m}}` | 直前の文字がn回以上m回以下の繰り返し | `'a{{2,3}}'` → `aa`, `aaa` |
| `|` | いずれかのパターンに一致(OR) | `'Taro|Hanako'` → `Taro`または`Hanako` |
| `\d` | 数字1文字(MySQL 8.0.4以降) | `'\d{{3}}'` → 数字3桁 |
| `\s` | 空白文字1文字(MySQL 8.0.4以降) | `'a\sb'` → `a b` |

### トランザクション

| SQL | 説明 | 例文 |
| --- | --- | --- |
| START TRANSACTION | 一連の処理をまとめて実行する準備をする | `START TRANSACTION;` |
| COMMIT | トランザクション内の変更を確定する | `COMMIT;` |
| ROLLBACK | トランザクション内の変更を取り消す | `ROLLBACK;` |

### 権限管理

| SQL | 説明 | 例文 |
| --- | --- | --- |
| GRANT | ユーザに権限を付与する | `GRANT SELECT, INSERT ON {selectdb}.users TO 'user1'@'%';` |
| GRANT(全権限) | 対象データベースの全ての操作権限を付与する | `GRANT ALL PRIVILEGES ON {selectdb}.* TO 'user1'@'%';` |
| REVOKE | ユーザから権限を剥奪する | `REVOKE INSERT ON {selectdb}.users FROM 'user1'@'%';` |
| FLUSH PRIVILEGES | 権限変更をサーバーに即時反映する | `FLUSH PRIVILEGES;` |
| SHOW GRANTS | ユーザに付与されている権限を確認する | `SHOW GRANTS FOR 'user1'@'%';` |


## データ型一覧

| 型 | 説明 | 例 |
| --- | --- | --- |
| INT | 整数値を格納する | `age INT` |
| SMALLINT / BIGINT | INTより格納できる範囲が小さい／大きい整数型 | `age SMALLINT` |
| DECIMAL(m,d) | 誤差のない正確な固定小数点数を格納する(金額など精度が重要な値向け) | `price DECIMAL(10,2)` |
| FLOAT / DOUBLE | 近似値として扱われる浮動小数点数を格納する | `score FLOAT` |
| VARCHAR(n) | 可変長文字列を格納する(最大n文字) | `name VARCHAR(100)` |
| CHAR(n) | 固定長文字列を格納する(n文字に満たない場合は空白で埋められる) | `code CHAR(4)` |
| TEXT | VARCHARより長い文字列を格納する | `description TEXT` |
| DATE | 日付を格納する(`YYYY-MM-DD`) | `birthday DATE` |
| DATETIME / TIMESTAMP | 日付と時刻を格納する | `created_at DATETIME` |
| BOOLEAN | 真偽値を格納する(内部的には0または1のTINYINTとして扱われる) | `is_active BOOLEAN` |


## 補足

- 文字列や日付は `'` (シングルクォート) 又は `"` (ダブルクォート) で囲む。
- 予約語やスペースを含む識別子は`` ` ``(バッククォート)で囲む。
- 1行コメントは`-- `(ハイフン2つ＋半角スペース)、複数行コメントは`/* ... */`で記述する。
