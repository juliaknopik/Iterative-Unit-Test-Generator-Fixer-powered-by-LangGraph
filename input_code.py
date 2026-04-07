def get_adult_users(users):
    # This function should return a list of user names that are 18 years or older. 
    # users is a list of dictionaries, e.g., [{'name': 'Ann', 'age': 25}, {'name': 'Tom', 'age': 15}]
    
    adults = []
    for user in users:
        if user['age'] >= 18:
            adults.append(user['name'])
    return adults