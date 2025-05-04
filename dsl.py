from typing import Any, Union, Dict
from .base import (SQLCondition, AndCondition, OrCondition, NotCondition, IsNull, IsNotNull, TrueCondition, 
FalseCondition, SQLExpression, col, cols, num, text, set_expr, Func, text_exprs)

"""
expressQL DSL — quick access to expressions, conditions, and helper guides.

>>> expressions_guide()
>>> conditions_guide()

You can build expressions and conditions interactively.
"""

def expressions_guide():
    """
    This function provides a guide to the different types of expressions
    that can be used in SQL conditions """

    #Make a single col object
    col1 = col("column1")
    #Make a list of col objects
    col2, col3, col4 = cols("column2", "column3", "column4")
    #alternatively
    col5, col6, col7 = cols("col5, col6, col7")

    #It's barely ever necessary to specify that a number or a string is a value, it will be inferred
    #But if you want to be explicit you can use num or text
    #num50 = num(50) #This is a number
    #text_hello = text("hello") #This is a string
    
    #If you have custom variables such as PI or E you can use col too.
    #col basically tells expressQL "Don't quote this string nor make it a placeholder"
    pi, e = cols("PI", "E")

    #To use functions in SQL you can use Func, both custom and built-in
    my_func = Func("MY_FUNCTION", col1, col2, col3)
    #You can also use built-in functions like SUM, AVG, etc.
    sum_func = Func("SUM", col1)

    #You can also directly import any builtin function from functions.py
    #from expressQL.functions import SUM
    #sum_func = SUM(col1, col2+30, abs(col3))

    #Any expression, no matter how complex, can be set
    complex_cond = (col1 + abs(col2) - 50/col3)*Func("LOG", col4) + col5*col6/col7
    #Operator | makes a concatenation of two expressions
    myconcat = col1 | " " | col2

    print(complex_cond.placeholder_pair()) #This will show the placeholders and their values
    #'((column1+1/ABS(column2)-?/column3)*LOG(column4)+(col5*col6)/col7)', [50]
    print(myconcat.placeholder_pair()) 
    #"(column1 || ' ' || column2)", []
def conditions_guide():
    """
    This function provides a guide to the different types of conditions
    that can be used in SQL queries.

    A basic condition is made of expressions and a comparison operator.
              - Comparison operators: ==, !=, <, <=, >, >=, between, not_between
              - Characteristiscs: is_null, is_not_null, like, not_like, in, not_in

    Compound conditions are made of basic conditions and logical operators.
              - Logical operators: and, or, not, xor
    """
    #let's get expressions
    weight, height = cols("weight", "height")
    #this makes another expression
    bmi = weight / (height ** 2)  # Body Mass Index
    #using an operator will make a condition
    bmi_condition = bmi < 25  # BMI less than 25

    print(bmi_condition.placeholder_pair())
    #('weight/POWER(height, ?) < ?', [2, 25])

    #If you have a custom function you can use it too
    bmi_condition = Func("BMI", weight, height) < 25  # BMI less than 25
    
    print(bmi_condition.placeholder_pair()) #This will show the placeholders and their values
    #'BMI(weight, height) < ?', [25]

    #You can check for sets
    address = col("address")
    felony_addresses = text_exprs({"felony_address1", "felony_address2", "felony_address3"})
    am_i_cooked = address.isin(felony_addresses)
    print(am_i_cooked.placeholder_pair()) #This will show the placeholders and their values

def primary_key_condition(pk_value: Dict) -> SQLCondition:

    """
    Constructs a primary key condition for a SQL query.
    This function generates a composite SQL condition by combining
    equality conditions for each key-value pair in the provided
    primary key dictionary. The conditions are combined using an
    AND logical operator.
    Args:
        pk_value (Dict): A dictionary representing the primary key,
                         where keys are column names and values are
                         the corresponding values to match.
    Returns:
        SQLCondition: A composite SQL condition object that can be
                      used in a query to filter rows based on the
                      primary key.
    """

    return AndCondition(
        *[(col(k) == v) for k, v in pk_value.items()]
    ) 

pk_condition = primary_key_condition