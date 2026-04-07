def get_adult_users(users):
    # This function returns a list of user names that are 18 years or older.
    # users is expected to be a list of dictionaries, e.g., [{'name': 'Ann', 'age': 25}, {'name': 'Tom', 'age': 15}]
    
    if not isinstance(users, list):
        raise ValueError("Input must be a list of dictionaries.")
    
    adults = []
    for user in users:
        if isinstance(user, dict):
            name = user.get('name')
            age = user.get('age')
            if isinstance(name, str) and isinstance(age, (int, float)) and age >= 18:
                adults.append(name)
    
    return adults