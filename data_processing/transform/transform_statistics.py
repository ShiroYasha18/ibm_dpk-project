from typing import Any

class TransformStatistics:
    """
    Basic statistics class collecting basic execution statistics.
    It can be extended for specific processors
    """

    def __init__(self):
        """
        Init - setting up variables. All of the statistics are collected in the dictionary.
        """
        self.stats = {
            "processing_time": 0.0,  # Initialize processing_time with a default value
        }

    def add_stats(self, stats: dict[str, Any]) -> None:
        """
        Add statistics
        :param stats - dictionary creating new statistics
        :return: None
        """
        for key, val in stats.items():
            if key in self.stats:
                self.stats[key] = self.stats.get(key, 0) + val
            else:
                self.stats[key] = val

    def get_execution_stats(self) -> dict[str, Any]:
        """
        Get execution statistics
        :return: The dictionary of stats
        """
        return self.stats
