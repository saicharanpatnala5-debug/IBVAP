"""
IBVAP - Risk Severity Classifier
Maps risk scores to operational severity bands.
"""
class SeverityClassifier:
    @staticmethod
    def classify(score: int) -> str:
        if score < 30:
            return "NORMAL"
        elif score < 60:
            return "LOW"
        elif score < 90:
            return "MEDIUM"
        elif score < 120:
            return "HIGH"
        else:
            return "CRITICAL"

severity_classifier = SeverityClassifier()
