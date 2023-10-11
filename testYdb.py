import sqlite3

class User:
    def __init__(self, id=None, username=None, email=None):
        self._id = id
        self._username = username
        self._email = email

    # Геттеры и сеттеры для атрибута id
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    # Геттеры и сеттеры для атрибута username
    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    # Геттеры и сеттеры для атрибута email
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    def __getattribute__(self, name):
        if name.endswith("_please"):
            return object.__getattribute__(self, name.replace("_please", ""))
        raise AttributeError("And the magic word!?")
    
    # Метод для сохранения объекта User в базу данных
    def save(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        if self.id is None:
            # Создаем новую запись
            cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)",
                           (self.username, self.email))
            self.id = cursor.lastrowid
        else:
            # Обновляем существующую запись
            cursor.execute("UPDATE users SET username = ?, email = ? WHERE id = ?",
                           (self.username, self.email, self.id))

        conn.commit()
        conn.close()

    # Метод для загрузки объекта User из базы данных по его id
    @classmethod
    def load(cls, id):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
        row = cursor.fetchone()

        if row is None:
            return None

        user = cls(id=row[0], username=row[1], email=row[2])

        conn.close()

        return user
    
    @classmethod
    def load(cls, filter_param=None, filter_value=None):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        query = "SELECT * FROM users"
        if filter_param:
            query += f" WHERE {filter_param} = ?"

        if filter_value:
            cursor.execute(query, (filter_value,))
        else:
            cursor.execute(query)

        rows = cursor.fetchall()

        users = []
        for row in rows:
            user = cls(id=row[0], username=row[1], email=row[2])
            users.append(user)

        conn.close()

        return users
    

# Создание объекта User
user = User(username='JohnDoe', email='john.doe@example.com')

# Сохранение в базу данных
user.save()

# Загрузка пользователя из базы данных по его id
loaded_user = User.load(user.id)

# Вывод данных пользователя
print(loaded_user.id)        # Вывод: id пользователя
print(loaded_user.username)  # Вывод: JohnDoe
print(loaded_user.email)     # Вывод: john.doe@example.com

# Загрузка всех пользователей с фильтром по имени пользователя (username)
users = User.load(filter_param='username', filter_value='JohnDoe')