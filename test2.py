# TEST 5: FULL PIPELINE - scores + explanation
print("\n" + "="*50)
print("TEST 5: FULL FRAMING EXPLANATION")
print("="*50)

from explainer import explain_framing

articles = [
    {
        "source": "Reuters",
        "headline": "Government announces new agricultural policy",
        "text": "The government today announced a new agricultural policy aimed at supporting rural farmers. Officials say the plan will be implemented in phases over the next year."
    },
    {
        "source": "OpinionPost",
        "headline": "Controversial farm law could devastate millions",
        "text": "The government may have allegedly rushed a controversial farm policy that critics warn could devastate small farmers. The dramatic move has reportedly shocked experts who claim it might cause irreversible damage to rural communities."
    },
    {
        "source": "NationalDaily",
        "headline": "Bold farm reform sparks heated debate",
        "text": "A bold and unprecedented agricultural reform has ignited fierce debate across the country. Sources say the government insists the policy is necessary, but opponents demand an immediate rollback of the alarming changes."
    }
]

explanation = explain_framing(articles)
print("\n", explanation)