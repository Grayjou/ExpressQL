from expressql import col, cols, Func

def arithmetic_comparisons():
    print("== Arithmetic Comparisons ==")
    age, salary, name = cols("age", "salary", "name")

    # Example 1: Simple age > 18
    cond1 = age > 18
    print("Age > 18:")
    print(cond1.sql_string())
    print(cond1.placeholder_pair())
    print()

    # Example 2: name starts with 'A' using LIKE
    cond2 = name.like("A%")
    print("Name starts with 'A':")
    print(cond2.sql_string())
    print(cond2.placeholder_pair())
    print()

    # Example 3: salary equals 5000
    cond3 = salary == 5000
    print("Salary == 5000:")
    print(cond3.sql_string())
    print(cond3.placeholder_pair())
    print()

def set_conditions():
    print("== Set Conditions ==")
    age, name = cols("age", "name")

    # Example 1: age IN (20, 30, 40)
    cond1 = age.isin([20, 30, 40])
    print("Age IN (20, 30, 40):")
    print(cond1.sql_string())
    print(cond1.placeholder_pair())
    print()

    # Example 2: name NOT IN ('Alice', 'Bob')
    cond2 = name.notin(['Alice', 'Bob'])
    print("Name NOT IN ('Alice', 'Bob'):")
    print(cond2.sql_string())
    print(cond2.placeholder_pair())
    print()

def function_conditions():
    print("== Function Expressions ==")
    name = col("name")
    height = col("height")
    # Example 1: UPPER(name) = 'ALICE'
    cond1 = Func("UPPER", name) == "ALICE"
    print("UPPER(name) = 'ALICE':")
    print(cond1.sql_string())
    print(cond1.placeholder_pair())
    print()

    # Example 2: LENGTH(name) > 5
    cond2 = Func("LENGTH", name) > 5
    print("LENGTH(name) > 5:")
    print(cond2.sql_string())
    print(cond2.placeholder_pair())
    print()

    con3 = Func("ABS", height + 100) < 200
    print("ABS(height + 100) < 200:")
    print(con3.sql_string())
    print(con3.placeholder_pair())

    print(name.startswith("A").sql_string())
    print(name.startswith("A").placeholder_pair())
    print()

def combining_conditions():
    print("== Combining Conditions ==")
    age = col("age")
    salary = col("salary")
    name = col("name")

    # Example 4: (age > 30 AND salary >= 4000)
    cond = (age > 30) * (salary >= 4000)
    print("Age > 30 AND salary >= 4000:")
    print(cond.sql_string())
    print(cond.placeholder_pair())
    print()

    # Example 5: (age < 25 OR name starts with 'J')
    cond = (age < 25) + name.like("J%")
    print("Age < 25 OR name starts with 'J':")
    print(cond.sql_string())
    print(cond.placeholder_pair())
    print()

def between_and_null_conditions():
    print("== BETWEEN and NULL Checks ==")
    age = col("age")
    date_of_birth = col("date_of_birth")

    cond1 = age.between(18, 65)
    print("Age BETWEEN 18 AND 65:")
    print(cond1.sql_string())
    print(cond1.placeholder_pair())
    print()

    cond2 = date_of_birth.is_null
    print("Date of birth IS NULL:")
    print(cond2.sql_string())
    print(cond2.placeholder_pair())
    print()

    cond3 = date_of_birth.is_not_null
    print("Date of birth IS NOT NULL:")
    print(cond3.sql_string())
    print(cond3.placeholder_pair())
    print()

def main():
    print("== Simple Examples ==")
    arithmetic_comparisons()
    #
    set_conditions()
    #
    function_conditions()
    #
    combining_conditions()
    #
    between_and_null_conditions()


if __name__ == "__main__":
    main()
