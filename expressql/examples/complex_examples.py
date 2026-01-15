from expressql import col, cols, Func, SQLChainCondition

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

    cond = (city.is_null() + region.isin(["North", "South"])) * ~(region == "East")
    print("City IS NULL OR region IN ('North', 'South') AND NOT region == 'East':")
    print(cond.sql_string())
    print(cond.placeholder_pair())
    print()

def not_in_and_not_like():
    print("== NOT IN and NOT LIKE Conditions ==")
    status = col("status")
    email = col("email")
    
    # Test the fixed is_not_in method
    cond1 = status.is_not_in(["inactive", "deleted", "archived"])
    print("Status NOT IN ('inactive', 'deleted', 'archived'):")
    print(cond1.sql_string())
    print(cond1.placeholder_pair())
    print()
    
    # NOT LIKE with wildcards
    cond2 = email.not_like("%@spam.com")
    print("Email NOT LIKE '%@spam.com':")
    print(cond2.sql_string())
    print(cond2.placeholder_pair())
    print()

def nested_arithmetic_and_functions():
    print("== Nested Arithmetic and Functions ==")
    price = col("price")
    quantity = col("quantity")
    discount = col("discount")
    
    # Complex calculation: total after discount with sales tax
    subtotal = price * quantity
    discount_amount = subtotal * (discount / 100)
    taxable_amount = subtotal - discount_amount
    sales_tax = taxable_amount * 0.08
    final_total = taxable_amount + sales_tax
    
    cond = final_total > 1000
    print("Complex pricing calculation (final_total > 1000):")
    print(cond.sql_string())
    print(cond.placeholder_pair())
    print()

def string_operations():
    print("== String Operations ==")
    first_name = col("first_name")
    last_name = col("last_name")
    email_domain = col("email_domain")
    
    # String concatenation with separator
    full_name = first_name | " " | last_name
    print("Full name concatenation:")
    print(full_name.sql_string())
    print(full_name.placeholder_pair())
    print()
    
    # Using string functions
    upper_email_cond = Func("UPPER", email_domain) == "COMPANY.COM"
    print("UPPER(email_domain) = 'COMPANY.COM':")
    print(upper_email_cond.sql_string())
    print(upper_email_cond.placeholder_pair())
    print()

def complex_date_conditions():
    print("== Complex Date and Time Conditions ==")
    created_at = col("created_at")
    updated_at = col("updated_at")
    current_date = Func("CURRENT_DATE")
    
    # Date arithmetic - records created in last 30 days
    days_diff = Func("JULIANDAY", current_date) - Func("JULIANDAY", created_at)
    cond1 = days_diff <= 30
    print("Records created in last 30 days:")
    print(cond1.sql_string())
    print(cond1.placeholder_pair())
    print()
    
    # Records updated after creation
    cond2 = updated_at > created_at
    print("Records updated after creation:")
    print(cond2.sql_string())
    print(cond2.placeholder_pair())
    print()

def subquery_conditions():
    print("== Subquery Conditions ==")
    employee_id = col("employee_id")
    department_id = col("department_id")
    
    # IN subquery
    subquery = "SELECT id FROM managers WHERE level > ?"
    cond1 = employee_id.is_in_subquery(subquery, [5])
    print("Employee IN (subquery):")
    print(cond1.sql_string())
    print(cond1.placeholder_pair())
    print()
    
    # NOT IN subquery
    inactive_depts = "SELECT id FROM departments WHERE active = ?"
    cond2 = department_id.not_in_subquery(inactive_depts, [False])
    print("Department NOT IN (inactive departments):")
    print(cond2.sql_string())
    print(cond2.placeholder_pair())
    print()

def aggregation_with_conditions():
    print("== Aggregation with Conditions ==")
    salary = col("salary")
    department = col("department")
    
    # Conditional aggregation using CASE-like logic
    avg_salary = Func("AVG", salary)
    max_salary = Func("MAX", salary)
    
    # Departments where average salary is above threshold
    cond1 = avg_salary > 75000
    print("AVG(salary) > 75000:")
    print(cond1.sql_string())
    print(cond1.placeholder_pair())
    print()
    
    # Combine with other conditions
    cond2 = (avg_salary > 75000) & (max_salary < 200000) & (department != "Executive")
    print("Complex aggregation condition:")
    print(cond2.sql_string())
    print(cond2.placeholder_pair())
    print()

def main():
    print("== Complex Examples ==")
    arithmetic_expressions()
    chained_conditions()
    advanced_functions()
    combined_logic()
    null_and_set_logic()
    not_in_and_not_like()
    nested_arithmetic_and_functions()
    string_operations()
    complex_date_conditions()
    subquery_conditions()
    aggregation_with_conditions()

if __name__ == "__main__":
    main()
