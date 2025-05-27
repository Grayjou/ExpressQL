from expressQL import col, cols, num, text, Func, SQLCondition, AndCondition, OrCondition, SQLChainCondition

def arithmetic_expressions():
    print("== Complex Arithmetic Expressions ==")
    age, weight, height = cols("age", "weight", "height")

    expr = (weight / (height ** 2)) * 703  # Body Mass Index in imperial units
    cond = expr < 25
    print("BMI < 25:")
    print(cond.sql_string())
    print(cond.placeholder_pair())
    print()

def chained_conditions():
    print("== Chained Conditions ==")
    score = col("score")

    cond = (50 < score) < 80   # Equivalent to 50 < score < 80
    print("cond",cond)
    print("50 < score < 80 (chained condition):")
    print(cond.sql_string())
    print(cond.placeholder_pair())
    print()

    col1, col2, col3 = cols("col1", "col2", "col3")
    chain = SQLChainCondition(col1, "<", col2, "<=", col3 + 75, "=", col1/col2 + 10)
    print("Chained condition with multiple columns:")
    print(chain.math_inequality())
    print(chain.placeholder_pair())
    print()

def advanced_functions():
    print("== Advanced Function Usage ==")
    salary = col("salary")
    bonus = col("bonus")

    total_income = salary + bonus
    cond = Func("LOG", total_income) > 10
    print("cond",cond)
    print("LOG(salary + bonus) > 10:")
    print(cond.sql_string())
    print(cond.placeholder_pair())
    print()

def combined_logic():
    print("== Combining Multiple Conditions ==")
    age, department = cols("age", "department")

    cond = ((age > 30) * (department == "HR")) + (department == "Finance")
    print("(age > 30 AND department == 'HR') OR department == 'Finance':")
    print(cond.sql_string())
    print(cond.placeholder_pair())
    print()

def null_and_set_logic():
    print("== NULL and SET Logic ==")
    city = col("city")
    region = col("region")

    cond = (city.is_null + region.isin(["North", "South"])) * ~(region == "East")
    print("City IS NULL OR region IN ('North', 'South') AND NOT region == 'East':")
    print(cond.sql_string())
    print(cond.placeholder_pair())
    print()

def main():
    print("== Complex Examples ==")
    arithmetic_expressions()
    chained_conditions()
    advanced_functions()
    combined_logic()
    null_and_set_logic()

if __name__ == "__main__":
    main()
