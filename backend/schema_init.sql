use AssetDB;
CREATE TABLE User(
    idUser INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(45),
    email VARCHAR(45) UNIQUE,
    role ENUM('user', 'admin')
);
CREATE TABLE Equipment(
    idEquipment INT PRIMARY KEY AUTO_INCREMENT,
    idUser INT,
    name VARCHAR(100),
    category VARCHAR(100),
    model VARCHAR(100),
    spec VARCHAR(255),
    supplier VARCHAR(100),
    purchase_date DATE,
    purchase_price DECIMAL(10,2),
    location VARCHAR(100),
    department VARCHAR(100),
    start_date DATE,
    warranty_expiry DATE,
    status ENUM('in_use','repairing','scrapped'),
    FOREIGN KEY (idUser) REFERENCES User(idUser)
);

CREATE TABLE Form (
    idForm INT PRIMARY KEY AUTO_INCREMENT,
    applicant_id INT,
    idEquipment INT,
    issue_description VARCHAR(255),
    status ENUM('pending','approved','rejected','repairing','completed'),
    reviewer_id INT,
    review_result ENUM('approved','rejected'),
    repair_start_date DATETIME,
    repair_end_date DATETIME,
    repair_description VARCHAR(255),
    repair_solution VARCHAR(255),
    repair_cost DECIMAL(10,2),
    repair_vendor VARCHAR(100),
    repair_person VARCHAR(100),
    FOREIGN KEY (applicant_id) REFERENCES User(idUser),
    FOREIGN KEY (reviewer_id) REFERENCES User(idUser),
    FOREIGN KEY (idEquipment) REFERENCES Equipment(idEquipment)
);