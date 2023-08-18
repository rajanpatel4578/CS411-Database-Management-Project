-- Create users table for my dashboard users
CREATE TABLE users(id mediumint auto_increment NOT NULL, username char(50) NOT NULL, PRIMARY KEY(id));

-- Create the users audit table to record the deletion of user account.
CREATE TABLE users_audit(deletedUID mediumint NOT NULL, deletedUsername CHAR(50), deletedBy VARCHAR(50) NOT NULL,time_stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(deletedUID, deletedUsername));

-- Trigger to maintain the users audit for deletion of user account.
delimiter //  
CREATE TRIGGER after_user_account_delete AFTER DELETE ON users
    FOR EACH ROW
    BEGIN 
    INSERT INTO users_audit(deletedUID, deletedUsername, deletedBy, time_stamp) VALUES(OLD.id, OLD.username, CURRENT_USER(), SYSDATE());
    END;//
delimiter ;

-- Create users favorite faculty table for my dashboard users
CREATE TABLE user_favorite_faculty ( uid mediumint, faculty_id int, PRIMARY KEY(uid, faculty_id), FOREIGN KEY(faculty_id) REFERENCES faculty(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY(uid) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE);

-- Create users favorite keywords table for my dashboard users
CREATE TABLE user_favorite_keyword ( uid mediumint, keyword_id int, PRIMARY KEY(uid, keyword_id), FOREIGN KEY(keyword_id) REFERENCES keyword(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY(uid) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE);

-- Create users favorite publications table for my dashboard users
CREATE TABLE user_favorite_publication (uid mediumint, publication_id int, PRIMARY KEY(uid,publication_id), FOREIGN KEY(publication_id) REFERENCES publication(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY(uid) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE);

-- Create users favorite university table for my dashboard users
CREATE TABLE user_favorite_university (uid mediumint, university_id int, PRIMARY KEY(uid, university_id), FOREIGN KEY(university_id) REFERENCES university(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY(uid) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE);

-- Create users affiliations table for my dashboard collaborations
CREATE TABLE user_affiliations (uid mediumint, university_id int, PRIMARY KEY(uid, university_id), FOREIGN KEY(university_id) REFERENCES university(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY(uid) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE);

-- Create users connections table for my dashboard collaborations
CREATE TABLE user_connections ( uid mediumint, faculty_id int, PRIMARY KEY(uid, faculty_id), FOREIGN KEY(faculty_id) REFERENCES faculty(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY(uid) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE);

-- Create users works table for my dashboard collaborations
CREATE TABLE user_work(uid mediumint, title varchar(512), pre_pub_id int auto_increment, PRIMARY KEY(pre_pub_id, uid, title), FOREIGN KEY(uid) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE);

-- Create users work keywords table for my dashboard collaborations
CREATE TABLE user_work_keyword(pre_pub_id int NOT NULL, keyword_id int NOT NULL, PRIMARY KEY(pre_pub_id,keyword_id), FOREIGN KEY(pre_pub_id) REFERENCES user_work(pre_pub_id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY(keyword_id) REFERENCES keyword(id) ON DELETE CASCADE ON UPDATE CASCADE);

-- Create users work publication citations table for my dashboard collaborations
CREATE TABLE user_work_publication_citations(pre_pub_id int NOT NULL, cited_publication_id int NOT NULL, PRIMARY KEY(pre_pub_id, cited_publication_id), FOREIGN KEY(pre_pub_id) REFERENCES user_work(pre_pub_id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY(cited_publication_id) REFERENCES publication(id) ON DELETE CASCADE ON UPDATE CASCADE);

-- Create view for top trending keywords since 2015
CREATE VIEW top_trending_keywords_last_5_years AS SELECT name FROM keyword, publication_keyword, publication WHERE publication_keyword.publication_id=publication.id AND keyword.id=publication_keyword.keyword_id AND publication.year >= (SELECT YEAR(CURDATE()) - 5) GROUP BY keyword_id ORDER BY COUNT(publication_id) DESC LIMIT 10;

--  Create view for trending University Research Keywords
CREATE VIEW university_trends AS SELECT university.name AS University, year, keyword.name AS Keyword, publication.id AS pub_id FROM faculty, university, faculty_publication, publication, publication_keyword, keyword WHERE university_id = university.id AND faculty.id = faculty_id AND publication.id = faculty_publication.publication_id AND publication.id = publication_keyword.publication_id AND keyword_id = keyword.id;
