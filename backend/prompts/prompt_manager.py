import yaml
import os
from typing import Dict, Any

class PromptManager:
    def __init__(self, yaml_file: str = None):
        if yaml_file is None:
            # Default to prompts.yaml in the same directory
            yaml_file = os.path.join(os.path.dirname(__file__), 'prompts.yaml')
        self.prompts = self._load_prompts(yaml_file)
    
    def _load_prompts(self, yaml_file: str) -> Dict[str, Any]:
        """Load prompts from YAML file."""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise Exception(f"Prompt file {yaml_file} not found")
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing YAML file: {e}")
    
    def get_system_prompt(self, agent_name: str) -> str:
        """Get system prompt for an agent."""
        return self.prompts.get(agent_name, {}).get('system', '')
    
    def get_user_prompt(self, agent_name: str, **kwargs) -> str:
        """Get formatted user prompt for an agent."""
        template = self.prompts.get(agent_name, {}).get('user_template', '')
        return template.format(**kwargs)
    
    def get_combined_prompt(self, agent_name: str, **kwargs) -> Dict[str, str]:
        """Get both system and formatted user prompt."""
        return {
            'system': self.get_system_prompt(agent_name),
            'user': self.get_user_prompt(agent_name, **kwargs)
        }

# Global instance
prompt_manager = PromptManager()