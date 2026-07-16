import json
import logging
from typing import Optional, List, Dict, Any
import re

logger = logging.getLogger(__name__)


class Skill:
    """Represents a skill extracted from job description."""

    def __init__(self, name: str, proficiency: str = "mid", required: bool = False):
        self.name = name
        self.proficiency = proficiency  # "junior", "mid", "senior"
        self.required = required

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "proficiency": self.proficiency,
            "required": self.required
        }

    def __repr__(self) -> str:
        return f"Skill(name={self.name}, proficiency={self.proficiency}, required={self.required})"


class LLMSkillInference:
    """Extract skills from job descriptions using Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM skill inference service.

        Args:
            api_key: Anthropic API key (if None, will try to use env variable)
        """
        self.api_key = api_key
        self._client = None
        self._skill_cache: Dict[str, List[Skill]] = {}

    @property
    def client(self):
        """Lazy-load Anthropic client."""
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                logger.error("anthropic package not installed. Install with: pip install anthropic")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                return None
        return self._client

    def extract_skills_from_jd(self, jd_text: str, technology: str = "") -> List[Skill]:
        """
        Extract technical skills from job description using Claude.

        Args:
            jd_text: Job description text
            technology: Technology category/field (Oracle, Python, etc.)

        Returns:
            List of Skill objects
        """
        if not jd_text or not jd_text.strip():
            logger.warning("Empty job description provided")
            return []

        cache_key = f"{jd_text[:100]}_{technology}"
        if cache_key in self._skill_cache:
            return self._skill_cache[cache_key]

        if not self.client:
            logger.warning("Anthropic client not available, falling back to regex extraction")
            return self._fallback_skill_extraction(jd_text, technology)

        try:
            prompt = f"""Extract technical skills from this job description.
Return a JSON object with:
- skills: list of {{name, proficiency ("junior"/"mid"/"senior"), required (bool)}}
- job_level: overall level ("entry"/"mid"/"senior")
- key_technologies: list of main technology areas

Job Description:
{jd_text[:2000]}

Technology Field: {technology}

Return ONLY valid JSON, no other text."""

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text
            result = json.loads(result_text)

            skills = [
                Skill(
                    name=s.get("name", "").strip(),
                    proficiency=s.get("proficiency", "mid").lower(),
                    required=s.get("required", False)
                )
                for s in result.get("skills", [])
                if s.get("name", "").strip()
            ]

            self._skill_cache[cache_key] = skills
            logger.debug(f"Extracted {len(skills)} skills from JD")
            return skills

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Claude response as JSON: {e}, using fallback")
            return self._fallback_skill_extraction(jd_text, technology)
        except Exception as e:
            logger.error(f"Failed to extract skills via Claude: {e}, using fallback")
            return self._fallback_skill_extraction(jd_text, technology)

    def _fallback_skill_extraction(self, jd_text: str, technology: str) -> List[Skill]:
        """
        Fallback: Extract skills using regex patterns.

        Args:
            jd_text: Job description text
            technology: Technology field

        Returns:
            List of Skill objects
        """
        combined_text = f"{technology} {jd_text}".lower()

        skill_patterns = {
            "Oracle": (["oracle"], "senior", True),
            "Java": (["java", "j2ee"], "mid", True),
            "Python": (["python"], "mid", False),
            "SQL": (["sql", "plsql", "oracle sql"], "mid", True),
            "Fusion": (["oracle fusion", "fusion hcm", "fusion scm"], "senior", True),
            "HCM": (["hcm", "human capital"], "mid", True),
            "APEX": (["apex", "oracle apex"], "mid", True),
            "JavaScript": (["javascript", "js"], "mid", False),
            "React": (["react", "react.js"], "mid", False),
            "Spring": (["spring", "spring boot"], "mid", False),
        }

        skills = []
        for skill_name, (patterns, proficiency, required) in skill_patterns.items():
            for pattern in patterns:
                if pattern in combined_text:
                    skills.append(Skill(name=skill_name, proficiency=proficiency, required=required))
                    break

        logger.debug(f"Fallback extraction found {len(skills)} skills")
        return skills

    def normalize_skills(self, skills: List[str]) -> List[str]:
        """
        Normalize skill names.

        Args:
            skills: List of skill names

        Returns:
            List of normalized skill names
        """
        normalized = []
        for skill in skills:
            skill = skill.strip().lower()
            skill_map = {
                "python3": "python",
                "py": "python",
                "js": "javascript",
                "ts": "typescript",
                "sql server": "sql",
                "oracle sql": "sql",
                "react.js": "react",
                "node.js": "nodejs",
                "spring boot": "spring",
            }
            normalized.append(skill_map.get(skill, skill))

        return normalized

    def skill_categories(self, skills: List[Skill]) -> Dict[str, List[str]]:
        """
        Categorize skills by type.

        Args:
            skills: List of Skill objects

        Returns:
            Dictionary mapping category to list of skill names
        """
        categories = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "tools": [],
            "other": []
        }

        category_keywords = {
            "languages": ["java", "python", "javascript", "typescript", "kotlin", "c#", "ruby", "golang", "rust"],
            "frameworks": ["spring", "react", "angular", "django", "flask", "fastapi", "oracle", "fusion"],
            "databases": ["sql", "oracle", "postgresql", "mysql", "mongodb", "elasticsearch"],
            "tools": ["docker", "kubernetes", "jenkins", "git", "maven", "gradle", "npm"],
        }

        for skill in skills:
            skill_name_lower = skill.name.lower()
            categorized = False

            for category, keywords in category_keywords.items():
                if any(kw in skill_name_lower for kw in keywords):
                    categories[category].append(skill.name)
                    categorized = True
                    break

            if not categorized:
                categories["other"].append(skill.name)

        return {k: v for k, v in categories.items() if v}

    def clear_cache(self) -> None:
        """Clear skill extraction cache."""
        self._skill_cache.clear()
