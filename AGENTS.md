# Critical Rules - MUST FOLLOW

**CRITICAL**: These rules are mandatory. Non-compliance will result in rejected
code.

---

## Rule 1: File Naming Conventions

### Markdown Files

**YOU MUST:**

- Use lowercase letters ONLY
- Use underscores to separate words
- Use `.md` extension (NOT `.MD` or `.markdown`)
- Exception: `README.md` is the ONLY uppercase filename allowed

**Examples:**

```text
CORRECT:
   docs/architecture_overview.md
   docs/how_to_setup.md
   README.md (only exception)

WRONG:
   docs/Architecture-Overview.md
   docs/ArchitectureOverview.md
   docs/ARCHITECTURE.md
   docs/architecture.MD
```

### YAML Files

**YOU MUST:**

- Use `.yaml` extension (NOT `.yml`)
- Apply to ALL YAML files without exception

**Examples:**

```text
CORRECT:
   config/production.yaml
   docker-compose.yaml
   .github/workflows/ci.yaml

WRONG:
   config/production.yml
   docker-compose.yml
```

---

## Rule 2: Code Quality Gates

**ALL of these MUST pass before claiming task complete:**

```bash
# 1. Lint and type check (enforces code quality)
ruff check src/

# 2. Format code (auto-fixes issues)
ruff format src/

# 3. Tests (must pass with >80% coverage)
pytest --cov=src --cov-report=html --cov-fail-under=80 --cov-report=term-missing

# 4. Markdown linting (ensures consistent formatting)
markdownlint --fix --config .markdownlint.json "${FILE}"
prettier --write --parser markdown --prose-wrap always "${FILE}"
```

**Expected Results:**

```text
ruff check src/  → "All checks passed!" or no output
ruff format src/ → "X files left unchanged" or "X files reformatted"
pytest           → "passed, 80% coverage"
```

**IF ANY FAIL**: Stop immediately and fix before proceeding.

---

## Rule 3: Documentation is Mandatory

**YOU MUST:**

1. **Doc Comments for ALL Public Items**

```python
def function(param: Type) -> Type:
    """Brief description of function.

    Args:
        param: Description of parameter

    Returns:
        Description of return value

    Raises:
        ErrorType: When condition occurs

    Examples:
        >>> result = function(arg)
        >>> assert result == expected
    """
    # Implementation
```

1. **Implementation Documentation File**

   - Create in `docs/explanation/` for EVERY feature/task
   - Use filename pattern: `{feature_name}_implementation.md`
   - Include: Overview, Components, Implementation Details, Testing, Examples

2. **Code Block Language Identifiers**
   - ALWAYS specify language in markdown code blocks
   - Use triple backticks with language name

**NEVER:**

- Skip documentation because "code is self-documenting"
- Omit language identifiers in code blocks
- Leave public APIs undocumented

---

## Rule 4: Error Handling Patterns

**YOU MUST:**

- Use custom exception classes for domain errors
- Raise exceptions for error conditions
- Document exceptions in docstrings
- Use context managers for resource cleanup

**NEVER:**

- Use bare `except:` clauses
- Ignore exceptions silently
- Return None to indicate errors
- Use assertions for validation

**Correct Pattern:**

```python
class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass

class ConfigReadError(ConfigError):
    """Raised when config file cannot be read."""
    pass

def load_config(path: str) -> Config:
    """Load configuration from file.

    Args:
        path: Path to config file

    Returns:
        Parsed configuration

    Raises:
        ConfigReadError: If file cannot be read
        ConfigError: If config is invalid
    """
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
    except IOError as e:
        raise ConfigReadError(f"Cannot read {path}: {e}")

    if not validate(data):
        raise ConfigError(f"Invalid config in {path}")

    return Config.from_dict(data)
```

---

## Rule 5: Testing Requirements

**YOU MUST:**

- Write tests for ALL public functions
- Test both success AND failure cases
- Test edge cases and boundary conditions
- Achieve >80% code coverage
- Use descriptive test names

**Test Structure:**

```python
import pytest
from mymodule import function

class TestFunction:
    def test_with_valid_input(self):
        """Test function with valid input."""
        # Arrange
        input_data = create_valid_input()

        # Act
        result = function(input_data)

        # Assert
        assert result == expected_value

    def test_with_invalid_input(self):
        """Test function raises error with invalid input."""
        with pytest.raises(ValueError):
            function(invalid_input)

    def test_edge_case(self):
        """Test function with boundary conditions."""
        result = function(edge_case_input)
        assert result is not None
```

---

## Rule 6: Git Commit Conventions

**DO NOT PERFORM GIT OPERATIONS UNLESS ASKED**

**Format:**

```text
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Rules:**

1. Type MUST be: `feat|fix|docs|style|refactor|perf|test|chore`
2. Description MUST be lowercase
3. Description MUST use imperative mood ("add" not "added")
4. First line MUST be ≤72 characters

**Examples:**

```text
CORRECT:
feat(auth): add JWT token refresh endpoint
fix(api): handle edge case in validation
docs(readme): update installation steps

WRONG:
Added JWT token (proj-1234)          # Wrong mood, no type
feat: add jwt (PROJ-1234)            # Missing scope
add jwt refresh (PROJ-1234)          # No type
```

---

## Rule 7: No Emojis

**YOU MUST:**

- Write ALL documentation without emojis
- Write ALL code comments without emojis
- Write ALL commit messages without emojis

**NEVER:**

- Use emojis in code
- Use emojis in documentation
- Use emojis in commit messages

---

## Rule 8: Documentation Quality Gates

**ALL markdown files MUST pass these quality gates:**

```bash
# 1. Check and fix markdown linting issues
markdownlint --fix --config .markdownlint.json "${FILE}"

# 2. Format markdown with prettier
prettier --write --parser markdown --prose-wrap always "${FILE}"
```

**YOU MUST:**

- Run markdownlint on ALL markdown files before committing
- Run prettier on ALL markdown files to ensure consistent formatting
- Fix any remaining linting errors that --fix cannot auto-correct
- Ensure prose wrapping is applied consistently

**Expected Results:**

```text
markdownlint → No output (all issues fixed) or specific errors to fix manually
prettier     → "1 file formatted" or "1 file unchanged"
```

**IF ANY FAIL**: Stop immediately and fix before proceeding.

**Apply to:**

- All new markdown files
- All modified markdown files
- Documentation in `docs/` directory
- README.md and other root-level markdown files

---

## Documentation Organization (Diataxis Framework)

**YOU MUST categorize documentation correctly:**

### Category 1: Tutorials (`docs/tutorials/`)

**Purpose**: Learning-oriented, step-by-step lessons

**Use for**:

- Getting started guides
- Learning path tutorials
- Hands-on examples

**Example**: `docs/tutorials/getting_started.md`

### Category 2: How-To Guides (`docs/how-to/`)

**Purpose**: Task-oriented, problem-solving recipes

**Use for**:

- Installation steps
- Configuration guides
- Troubleshooting procedures

**Example**: `docs/how-to/setup_monitoring.md`

### Category 3: Explanations (`docs/explanation/`) ← DEFAULT FOR YOUR SUMMARIES

**Purpose**: Understanding-oriented, conceptual discussion

**Use for**:

- Architecture explanations
- Design decisions
- Implementation summaries ← **YOU TYPICALLY CREATE THESE**
- Concept clarifications

**Example**: `docs/explanation/phase4_observability_implementation.md`

### Category 4: Reference (`docs/reference/`)

**Purpose**: Information-oriented, technical specifications

**Use for**:

- API documentation
- Configuration reference
- Command reference

**Example**: `docs/reference/api_specification.md`

### Decision Tree: Where to Put Documentation?

```text
Is it a step-by-step tutorial?
├─ YES → docs/tutorials/
└─ NO
   ├─ Is it solving a specific task?
   │  ├─ YES → docs/how-to/
   │  └─ NO
   │     ├─ Is it explaining concepts/architecture?
   │     │  ├─ YES → docs/explanation/  ← MOST COMMON FOR AI AGENTS
   │     │  └─ NO
   │     │     └─ Is it reference material?
   │     │        └─ YES → docs/reference/
```

## Copyright

Follow the [SPDX Spec](https://spdx.github.io/spdx-spec/) for copyright and
licensing information.

## Validation Checklist

**Before claiming task complete, verify ALL:**

- [ ] File naming follows conventions (lowercase_underscore.md, .yaml not .yml)
- [ ] All quality gates pass (format, check, lint, test)
- [ ] All markdown files pass markdownlint and prettier
- [ ] All public items have doc comments with examples
- [ ] Implementation documentation created in `docs/explanation/`
- [ ] No emojis in code, docs, or commits
- [ ] Commit message follows conventional format
- [ ] Error handling uses appropriate patterns
- [ ] Tests cover success, failure, and edge cases
- [ ] Code coverage >80%

---

## Emergency Quick Reference

**If you remember nothing else:**

1. **File Extensions**: `.yaml` NOT `.yml`, `.md` with lowercase_underscore
2. **Quality Gates**: All language-specific commands MUST pass
3. **Documentation**: Create file in `docs/explanation/` with implementation
   summary

**These three rules will prevent 90% of rejections.**
