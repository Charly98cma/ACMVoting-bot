create_users_table = \
    '''CREATE TABLE IF NOT EXISTS registered_users(
    telegramID VARCHAR(64) PRIMARY KEY NOT NULL,
    alias VARCHAR(64) NOT NULL,
    fullName VARCHAR(64) NOT NULL);'''

create_vote_table = \
    '''CREATE TABLE IF NOT EXISTS votes_table(
    candidate VARCHAR(64) PRIMARY KEY NOT NULL,
    votes INT NOT NULL,
    UNIQUE(candidate));'''

insert_candidate = \
    '''INSERT OR IGNORE INTO votes_table(candidate, votes)
    VALUES (?, ?)'''

check_user_registered = \
    '''SELECT * FROM registered_users WHERE telegramID=:id'''

register_user = \
    '''INSERT INTO registered_users values (:telegramid, :alias, :fullname)'''

check_user_voted = \
    '''SELECT votado FROM registered_users WHERE telegramID=:id'''

register_user_vote = \
    '''UPDATE registered_users SET votado=1 WHERE telegramID=?'''

update_vote = \
    '''UPDATE votes_table SET votes=votes+1 WHERE candidate=?'''
