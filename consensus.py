from structure import Receipt


class ConsensusEngine:

    def merge(self, results: list[dict]):

        final = {}

        for field in Receipt.model_fields.keys():

            candidates = [
                getattr(r, field)
                for r in results
                if getattr(r, field, None) is not None
            ]

            final[field] = max(
                candidates,
                key=lambda x: x.confidence,
                default=None
            )

        return Receipt(**final)