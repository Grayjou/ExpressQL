**expressQL** — Build complex SQL expressions in pure Python with safe, intuitive syntax.

**expressQL** is a flexible, Pythonic Domain-Specific Language (DSL) for constructing complex SQL conditions and expressions safely and expressively.  
It is designed to reduce boilerplate, prevent common SQL mistakes, and allow arithmetic, logical, and chained comparisons directly in Python syntax.

## Features

✅ Arithmetic expressions with automatic SQL translation  
✅ Logical composition (AND, OR, NOT) using natural Python operators  
✅ Chained inequalities (`50 < col("age") < 80`)  
✅ SQL-safe placeholder management  
✅ Null-safe operations (`is_null`, `not_null`)  
✅ Set membership (`IN`, `NOT IN`)  
✅ Supports custom SQL functions (`Func(...)`)  
✅ Fluent API for advanced condition building

## Quick Example

```python
from expressql import col, cols, Func

age, salary, department = cols("age", "salary", "department")

condition = ((age > 30) * (department == "HR")) + (salary > 50000)
#alternatively
#condition = ((age > 30) & (department == "HR")) & (salary > 5000)

print(condition.placeholder_pair())
# ('((age > ?) AND (department = ?)) OR (salary > ?)', [30, 'HR', 50000])
```

## Installation

```bash
pip install expressql
```

## Key Concepts

### 1️⃣ Expressions & Comparisons

```python
from expressql import col

age = col("age")
condition = (age + 10) > 50
```

SQL:
```sql
(age + 10) > 50
```

### 2️⃣ Chained Conditions

```python
score = col("score")
cond = (50 < score) < 80  # Equivalent to 50 < score < 80
```

SQL:
```sql
(score > 50 AND score < 80)
```

### 3️⃣ Logical Composition

Use `*` or `&` for **AND**, `+` or `|` for **OR**, and `~` for **NOT**:

```python
salary = col("salary")
dept = col("department")
cond = (salary > 40000) * (dept == "IT")
```

SQL:
```sql
(salary > 40000 AND department = 'IT')
```

### 4️⃣ Functions
Functions can be called directly on expressions if they are Uppercase

```python
from expressql import Func, col, cols

total = col("salary") + col("bonus")
cond = total.LOG() > 10
# Equivalent to LOG(salary + bonus) > 10
```

SQL:
```sql
LOG((salary + bonus)) > 10
```
Easy function expressions:
```python
name, SSN, birthday = cols("name","SSN", "birthday")
average = name.CONCAT(SSN, "birthday", col("age") + 10)

print(average.placeholder_pair())
>>> CONCAT(SSN, birthday, age + ?) , [10]
```
SQL:
```SQL
CONCAT(name, SSN, birthday, age + 10)
```

You can also declare any custom function like this 
```python
from expressQL import functions as f, cols
salary, bonus, passive_incomes = cols("salary", "bonus", "passive_incomes")
f.CUSTOM_FUNC_FOO(salary, bonus, passive_incomes, inverted = True)
```

```SQL
1/CUSTOM_FUNC_FOO(salary, bonus, passive_incomes)
```
### 5️⃣ NULL and Set Operations

```python
city = col("city")
region = col("region")

cond = city.is_null + region.isin(["North", "South"])
```

SQL:
```sql
(city IS NULL OR region IN ('North', 'South'))
```

## Advanced Usage

Check the provided examples:

- [simple_examples.py](./simple_examples.py)
- [complex_examples.py](./complex_examples.py)

```bash
python simple_examples.py
python complex_examples.py
```

These showcase arithmetic, chains, null logic, function usage, and complex logical combinations.

## FAQ

**Why doesn't expressQL include full query builders?**  
This module focuses on expressions and conditions. I will make (or probably already did) a module that integrates these functionalities into query building.

**Can you make the column name validation more permissive?**  
In most cases, strict column validation prevents SQL injection or typos. However, I have a version that does a simpler check and allows passing forgiven characters. If it proves relevant, I will probably update it.

**Every condition string comes wrapped in brackets, is there any way to avoid it?**
The conditions wrap themselves in brackets to pass it to other functions that might be calling it. Avoiding this could be implemented by setting a check '_first = True' into the functions, but it's just one extra pair of parenthesis on the final expression

> **🔥 Tip**  
> If you're using this in a larger query builder or ORM, let me know —  
> I might have an `expressQL-querybuilder` in the works 👀.

---

## Contributing

Contributions are welcome!  
If you have suggestions for improvements, new features, or find any bugs, feel free to open an issue or submit a pull request.  
I'm especially interested in ideas for better query builders and integrations with ORMs.

## Roadmap

- 📌 More built-in SQL functions (`expressQL.functions`)
- 📌 Chain-aware logical optimizations
- 📌 Full Query Builder integration (maybe `expressQL-querybuilder`)
- 📌 Async support and better placeholder systems (for more DB engines)
- 📌 Better error tracing and SQL preview options

## License

MIT License — free for personal and commercial use.
