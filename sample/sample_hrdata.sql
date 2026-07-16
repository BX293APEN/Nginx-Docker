-- ============================================================
-- データベース作成
-- ============================================================
CREATE DATABASE IF NOT EXISTS HRDB
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_general_ci;

USE HRDB;

-- ============================================================
-- テーブル定義
-- ============================================================
-- Employee.dno <-> Department.dno, Department.manager <-> Employee.eno
-- の相互参照があるため、テーブル作成時は外部キー制約チェックを一旦無効化する

SET FOREIGN_KEY_CHECKS = 0;

-- 社員テーブル
CREATE TABLE Employee (
    eno     CHAR(4)      NOT NULL,
    ename   VARCHAR(20)  NOT NULL,
    esalary INT          NOT NULL,
    dno     CHAR(1)      NOT NULL,
    PRIMARY KEY (eno),
    FOREIGN KEY (dno) REFERENCES Department(dno)
) ENGINE = InnoDB;

-- 部署テーブル
CREATE TABLE Department (
    dno     CHAR(1)      NOT NULL,
    dname   VARCHAR(20)  NOT NULL,
    manager CHAR(4)      NOT NULL,
    PRIMARY KEY (dno),
    FOREIGN KEY (manager) REFERENCES Employee(eno)
) ENGINE = InnoDB;

-- プロジェクトテーブル
CREATE TABLE Project (
    pno    VARCHAR(4)   NOT NULL,
    pname  VARCHAR(30)  NOT NULL,
    leader CHAR(4)      NOT NULL,
    PRIMARY KEY (pno),
    FOREIGN KEY (leader) REFERENCES Employee(eno)
) ENGINE = InnoDB;

-- プロジェクトメンバーテーブル
CREATE TABLE ProjectMember (
    pno    VARCHAR(4) NOT NULL,
    member CHAR(4)    NOT NULL,
    FOREIGN KEY (pno) REFERENCES Project(pno),
    FOREIGN KEY (member) REFERENCES Employee(eno)
) ENGINE = InnoDB;

-- ============================================================
-- データ登録
-- ============================================================

-- Employee
INSERT INTO Employee (eno, ename, esalary, dno) VALUES
('1001', '浅野', 800, 'D'),
('1002', '坂口', 600, 'D'),
('1003', '山口', 800, 'S'),
('1004', '森',   900, 'S'),
('1005', '田中', 700, 'S'),
('1006', '山田', 600, 'P');

-- Department
INSERT INTO Department (dno, dname, manager) VALUES
('D', '設計',   '1001'),
('S', '営業',   '1003'),
('P', '社長室', '1006');

-- Project
INSERT INTO Project (pno, pname, leader) VALUES
('東', '東プロジェクト', '1004'),
('西', '西プロジェクト', '1005');

-- ProjectMember
INSERT INTO ProjectMember (pno, member) VALUES
('東', '1001'),
('東', '1002'),
('東', '1003'),
('東', '1004'),
('西', '1002'),
('西', '1003'),
('西', '1005');

SET FOREIGN_KEY_CHECKS = 1;
