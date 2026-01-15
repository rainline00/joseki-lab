"""
Factory Boy factories for Joseki Manager tests.

テスト用のモデルファクトリを定義
後続フェーズでモデルが追加されたら、対応するファクトリをここに追加する
"""

import factory


class BaseFactory(factory.django.DjangoModelFactory):
    """
    基底ファクトリクラス

    すべてのモデルファクトリはこのクラスを継承する
    """

    class Meta:
        abstract = True


# 後続フェーズで追加するファクトリの例:
#
# class JosekiTreeFactory(BaseFactory):
#     class Meta:
#         model = "trees.JosekiTree"
#
#     name = factory.Sequence(lambda n: f"Tree {n}")
#     description = factory.Faker("text", max_nb_chars=200)
