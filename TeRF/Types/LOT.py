import TeRF.Types.TypedTRS as TTRS


class LOT(TTRS.TypedTRS):
    pass


if __name__ == '__main__':
    import TeRF.Test.test_grammars as tg
    lot = LOT(tg.types,
              tg.primitives,
              tg.semantics)
    print lot
