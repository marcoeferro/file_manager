# MassEdit

MassEdit is a batch file processing tool driven by YAML pipelines.

It allows you to:

- Edit text files in bulk
- Modify YAML frontmatter
- Move and organize files
- Run safely inside a sandbox
- Generate execution reports

---

## Features

- Declarative YAML configuration
- Regex-based transformations
- Metadata management
- Parallel execution
- Safe sandbox mode
- Detailed reports

---

## Installation

```bash
pip install -r requirements.txt
```
## Usage
```bash
python main.py --config config.yml
```

## Configuration
See CONFIG_SPEC.md for full reference.

## Examples
Check /examples directory.

## Safety
All filesystem operations are executed inside a sandbox before commit.

No real files are modified until commit.

## License
MIT


---

# 📁 `examples/`

## 1️⃣ `examples/basic_clean.yml`

Remove trailing spaces.

```yaml
version: "1.0.0"

project:
  root: "./notes"

plan:
  content:
    - operation: delete
      files: "**/*.md"
      mode: regex
      pattern: "\\s+$"

pipeline:
  - select
  - sandbox
  - plan
  - execute
  - commit
```