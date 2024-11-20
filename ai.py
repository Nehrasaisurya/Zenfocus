import json
import re
import google.generativeai as genai


genai.configure(api_key="AIzaSyCzHTHJtelwP2aVcmcHXu4JKWHcD-mT7sQ")


class UserThresholdSetter:
    def _init_(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

        self.total_thresholds = {
            "Coding/Development": {"total_usage_limit": None},
            "Entertainment": {"total_usage_limit": None},
            "Social Media": {"total_usage_limit": None},
            "Gaming": {"total_usage_limit": None},
            "Education": {"total_usage_limit": None},
            "Shopping": {"total_usage_limit": None},
            "Health & Fitness": {"total_usage_limit": None},
            "News": {"total_usage_limit": None},
            "Video Streaming": {"total_usage_limit": None},
            "Work/Productivity": {"total_usage_limit": None},
            "Unknown": {"total_usage_limit": 30}
        }

        self.continuous_thresholds = {
            "Coding/Development": {"continuous_usage_limit": None},
            "Entertainment": {"continuous_usage_limit": None},
            "Social Media": {"continuous_usage_limit": None},
            "Gaming": {"continuous_usage_limit": None},
            "Education": {"continuous_usage_limit": None},
            "Shopping": {"continuous_usage_limit": None},
            "Health & Fitness": {"continuous_usage_limit": None},
            "News": {"continuous_usage_limit": None},
            "Video Streaming": {"continuous_usage_limit": None},
            "Work/Productivity": {"continuous_usage_limit": None},
            "Unknown": {"continuous_usage_limit": 15}
        }

    def set_thresholds(self, user_responses):
        prompt = (
            f"Given these user responses: {json.dumps(user_responses)}, "
            "provide the recommended app usage thresholds in minutes and "
            "suggest 3 relevant break activities. "
            "Separate continuous and total usage with a blank line. "
            "Use this EXACT format:\n\n"
            "Category1: X\n"
            "Category2: Y\n"
            "\n"
            "Category1: A\n"
            "Category2: B\n\n"
            "Activity1\n"
            "Activity2\n"
            "Activity3"
        )

        response = self.model.generate_content(prompt)

        response_text = response.text.strip()
        print("Response Text:", response_text)

        continuous_thresholds = {}
        total_thresholds = {}
        break_activities = []

        try:

            sections = response_text.split('\n\n')
            continuous_section, total_section, activities_section = sections

            pattern = r"(\w+/\w+|\w+):\s*(\d+)"

            # Extract continuous thresholds
            continuous_matches = re.findall(pattern, continuous_section)
            for category, minutes in continuous_matches:
                continuous_thresholds[category] = {
                    "continuous_usage_limit": int(minutes)}

            # Extract total thresholds
            total_matches = re.findall(pattern, total_section)
            for category, minutes in total_matches:
                total_thresholds[category] = {
                    "total_usage_limit": int(minutes)}

            # Extract break activities
            break_activities = [activity.strip()
                                for activity in activities_section.splitlines()]

        except ValueError:
            print("Error: Unexpected response format from AI model.")
            return None  # Or handle the error as needed

        # Convert thresholds to JSON strings and write to files
        continuous_thresholds_json = json.dumps(
            continuous_thresholds, indent=4)
        total_thresholds_json = json.dumps(total_thresholds, indent=4)

        with open('continuous_thresholds.json', 'w') as f:
            f.write(continuous_thresholds_json)
        with open('total_thresholds.json', 'w') as f:
            f.write(total_thresholds_json)

        return {
            "continuous_usage_thresholds": continuous_thresholds,
            "total_usage_thresholds": total_thresholds,
            "break_activities": break_activities
        }


# Example usage
if __name__ == "_main_":
    # Load the user responses from a JSON variable (or a file)
    user_responses = {
        "name": "Lavanya",
        "gender": "Female",
        "screenTime": "4-6",  # This can be interpreted later
        "primarlyUsed": [
            "Shopping",
            "Education",
            "Gaming",
            "Entertainment"
        ],
        "interestedBreaks": [
            "Move away from screen",
            "Exercise",
            "Meditation",
            "Puzzles/Games",
            "Soothing Music"
        ],
        "primaryGoal to install our app": "To reduce stress and increase productivity"
    }

    threshold_setter = UserThresholdSetter()

    user_thresholds = threshold_setter.set_thresholds(user_responses)

    if user_thresholds:
        print("User thresholds and break activities saved to JSON files (if successful).")
    else:
        print("Failed to generate user thresholds.")
