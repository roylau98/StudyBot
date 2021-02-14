import sqlite3


class DataBase:
    def __init__(self, database):
        self.database = database
        self.connect()
        self.setup()

    def connect(self):
        """
        connects to the sqlite3 database, and create the cursor class
        :return: NIL
        """
        self.connection = sqlite3.connect(self.database, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        """
        closes the sqlite3 database connection
        :return: NIL
        """
        self.connection.close()

    def setup(self):
        """
        setups the database, checking if the table exists, if not creates it
        :return: NIL
        """
        sql_command = "CREATE TABLE IF NOT EXISTS questions_answers_bank (chat_id TEXT," \
                      "questions TEXT, " \
                      "answers TEXT, " \
                      "mods TEXT);"
        sql_command2 = "CREATE TABLE IF NOT EXISTS users (telegram_handle TEXT, mods TEXT);"
        self.cursor.execute(sql_command)
        self.cursor.execute(sql_command2)
        self.connection.commit()

    def add_questions(self, chat_id: str, question: str, mods: str):
        """
        adds questions into the database, categorised by the mods
        :param question: string
        :param mods: string
        :param chat_id: string
        :return: NIL
        """
        sql_command = "INSERT INTO questions_answers_bank (chat_id, questions, mods) VALUES (?, ?, ?);"
        data = (chat_id, question, mods, )
        self.cursor.execute(sql_command, data)
        self.connection.commit()

    def add_answer(self, question: str, answer: str):
        """
        search db for the question using exact string matching and add in the answer,
        update limit is 1 since only one question has exact string matching
        :param question: string
        :param answer: string
        :return: NIL
        """
        sql_command = "UPDATE questions_answers_bank SET answers = (?) WHERE rowid IN (" \
                      "SELECT rowid FROM questions_answers_bank WHERE questions = (?) LIMIT 1)"
        data = (answer, question)
        self.cursor.execute(sql_command, data)
        self.connection.commit()

    def search_answer(self, question: str) -> str:
        """
        When a user replied to a question the answer to it, we need to find the telegram handle of the person who
        asked the question so that we can directly reply to him/ her
        :return: the telegram handle of the user who asked the question
        """
        sql_command = "SELECT chat_id FROM questions_answers_bank WHERE questions = (?);"
        data = (question, )
        chatID = self.cursor.execute(sql_command, data).fetchone()[0]

        return chatID

    def filter_questions_unanswered(self) -> dict:
        """
        find all unanswered questions, sorted by mods
        :return: dictionary of questions list, with mods as the key
        """
        sql_command = "SELECT questions, mods FROM questions_answers_bank WHERE answers IS NULL OR answers = '';"
        questions = self.cursor.execute(sql_command).fetchall()
        question_dict = {}

        for q in questions:
            if q[1] in question_dict:
                question_dict[q[1]].append(q[0])
            else:
                question_dict[q[1]] = [q[0]]

        return question_dict

    def add_users(self, telegramHandle: str, mods: str):
        """
        add users in table users, with their telegram handle and mods of the mods they took
        creates a new row each time
        :param telegramHandle: string
        :param mods: string
        :return:
        """
        sql_command = "INSERT INTO users (telegram_handle, mods) VALUES (?, ?);"
        data = (telegramHandle, mods,)
        self.cursor.execute(sql_command, data)
        self.connection.commit()

    def delete_mods(self, telegramHandle: str, mods: str):
        """
        delete mods tied to telegram handle if students are not taking the mod anymore
        :param telegramHandle: string
        :param mods: string
        :return:
        """
        sql_command = "DELETE FROM users WHERE rowid IN (" \
                      "SELECT rowid FROM users WHERE telegram_handle = (?) AND mods = (?) LIMIT 1);"
        data = (telegramHandle, mods,)
        self.cursor.execute(sql_command, data)
        self.connection.commit()

    def delete_all_users(self, telegramHandle: str):
        """
        used if user wishes to erase all data from database
        :param telegramHandle: string
        :return:
        """
        sql_command = "DELETE FROM users WHERE telegram_handle = (?);"
        data = (telegramHandle,)
        self.cursor.execute(sql_command, data)
        self.connection.commit()

    def find_all_users(self, mods: str) -> list:
        """
        finds all telegram_handle that are taking the same mods as the one who called it
        :param mods: string
        :return: list of telegram handles
        """
        sql_command = "SELECT DISTINCT (SELECT telegram_handle FROM users WHERE mods = (?));"
        data = (mods,)
        table = self.cursor.execute(sql_command, data)

        return [users[0] for users in table.fetchall()]


if __name__ == '__main__':
    db = DataBase("questions.db")
    db.add_questions("-", "How to find depth of binary tree", "CZ1107")
    db.add_questions("-", "How to add new nodes", "CZ1107")
    db.add_questions("-", "How to delete nodes not used", "CZ1107")
    db.add_questions("-", "How to get all grandchildren nodes in BST", "CZ1107")

    db.add_questions("-", "How to find determinants", "CZ1104")
    db.add_questions("-", "What is the standard matrix of transformation", "CZ1104")
    db.add_questions("-", "What is the N(A) and C(A) of a matrix", "CZ1104")
    db.add_questions("-", "What are free and independent variables", "CZ1104")

    db.add_questions("-", "How to do nested subroutines.", "CZ1106")
    db.add_questions("-", "Why do we use RRX and LSR instructions.", "CZ1106")
    db.add_questions("-", "What is the link register used for.", "CZ1106")
    db.add_questions("-", "Why is the PC always 8 bytes ahead?", "CZ1106")
    db.close_connection()
