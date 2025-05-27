```markdown
# expressQL — Build complex SQL expressions in pure Python with safe, intuitive syntax

**expressQL** is a flexible, Pythonic Domain-Specific Language (DSL) for constructing complex SQL conditions and expressions safely and expressively.  
It is designed to reduce boilerplate, prevent common SQL mistakes, and allow arithmetic, logical, and chained comparisons directly in Python syntax.

---

## 🚀 Features

✅ Arithmetic expressions with automatic SQL translation  
✅ Logical composition (AND, OR, NOT) using natural Python operators  
✅ Chained inequalities (`50 < col("age") < 80`)  
✅ SQL-safe placeholder management  
✅ Null-safe operations (`is_null`, `not_null`)  
✅ Set membership (`IN`, `NOT IN`)  
✅ Supports custom SQL functions (`Func(...)`)  
✅ Fluent API for advanced condition building  
✅ **Parsing of SQL-like strings into expressions and conditions**  
✅ **Automatic expansion of `BETWEEN` clauses into composite comparisons**

---

## ⚡ Quick Example

```python
from expressql import col, cols, Func

age, salary, department = cols("age", "salary", "department")

condition = ((age > 30) * (department == "HR")) + (salary > 50000)

print(condition.placeholder_pair())
# ('((age > ?) AND (department = ?)) OR (salary > ?)', [30, 'HR', 50000])
```

---

## 🧠 Parsing SQL-Like Strings

You can parse raw strings into full SQL-safe expressions:

```python
from expressql.parsers import parse_expression

expr = parse_expression("LOG(age, 10) + CUSTOM_FUNC(salary, bonus + 10) + 15")
print(expr.placeholder_pair())
# ('(? + LOG(age, ?) + CUSTOM_FUNC(salary, (bonus + ?)))', [15, 10, 10])
```

Or transform high-level condition strings:

```python
from expressql.parsers import parse_condition

cond = parse_condition("age BETWEEN 30 AND 50 AND department = 'IT'")
print(cond.placeholder_pair())
# ('(age >= ? AND age <= ?) AND (department = ?)', [30, 50, 'IT'])
```

Auto-convert `BETWEEN` clauses:

```python
from expressql.parsers import transform_betweens

s = "weight/POWER(height, 2) BETWEEN 18.5 AND 24.9 AND age >= 18"
print(transform_betweens(s))
# '(weight / POWER(height, 2) >= 18.5 AND weight / POWER(height, 2) <= 24.9 AND age >= 18)'
```

---

## 🧩 Key Concepts

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

Functions can be called directly on expressions if they are uppercase:

```python
from expressql import col

total = col("salary") + col("bonus")
cond = total.LOG() > 10
```

SQL:
```sql
LOG((salary + bonus)) > 10
```

Custom functions:

```python
from expressql import functions as f, cols

salary, bonus, passive_incomes = cols("salary", "bonus", "passive_incomes")
func_expr = f.CUSTOM_FUNC_FOO(salary, bonus, passive_incomes, inverted=True)
```

SQL:
```sql
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

---

## 🧪 Advanced Usage

Check the provided examples:

- [simple_examples.py](.examples/simple_examples.py)
- [complex_examples.py](.examples/complex_examples.py)

```bash
python simple_examples.py
python complex_examples.py
```

These demonstrate arithmetic, chaining, null logic, function use, and condition parsing.

---

## FAQ

**Why doesn't expressQL include full query builders?**  
This module focuses on expressions and conditions. For record queries with SELECT, UPDATE, etc, with joins and so on, I have made recordsQL and am working on tablesQLite

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