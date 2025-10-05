from typing import Type, Optional

from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import (
    PrivateL1SharedL2CacheHierarchy,
)
from gem5.utils.override import overrides


class CustomPrivateL1SharedL2CacheHierarchy(PrivateL1SharedL2CacheHierarchy):
    def __init__(
        self,
        l1_replacement_policy=None,
        l2_replacement_policy=None,
        l1_prefetcher=None,
        l2_prefetcher=None,
        l1_size="32kB",
        l2_size="256kB",
        l1_assoc=2,
        l2_assoc=8,
    ):
        super().__init__(
            l1i_size=l1_size,
            l1d_size=l1_size,
            l2_size=l2_size,
            l1i_assoc=l1_assoc,
            l1d_assoc=l1_assoc,
            l2_assoc=l2_assoc,
        )
        self._l1_size = l1_size
        self._l2_size = l2_size
        self._l1_assoc = l1_assoc
        self._l2_assoc = l2_assoc
        self._l1_replacement_policy = l1_replacement_policy
        self._l2_replacement_policy = l2_replacement_policy
        self._l1_prefetcher = l1_prefetcher
        self._l2_prefetcher = l2_prefetcher

    @overrides(PrivateL1SharedL2CacheHierarchy)
    def incorporate_cache(self, board) -> None:
        super().incorporate_cache(board)

        for l1i in self.l1icaches:
            if self._l1_replacement_policy:
                if hasattr(self._l1_replacement_policy, "constituency_size"):
                    l1i.replacement_policy = self._l1_replacement_policy(
                        constituency_size=self._l1_size
                    )
                else:
                    l1i.replacement_policy = self._l1_replacement_policy()
            if self._l1_prefetcher:
                l1i.prefetcher = self._l1_prefetcher()

        for l1d in self.l1dcaches:
            if self._l1_replacement_policy:
                if hasattr(self._l1_replacement_policy, "constituency_size"):
                    l1d.replacement_policy = self._l1_replacement_policy(
                        constituency_size=self._l1_size
                    )
                else:
                    l1d.replacement_policy = self._l1_replacement_policy()
            if self._l1_prefetcher:
                l1d.prefetcher = self._l1_prefetcher()

        if self._l2_replacement_policy:
            if hasattr(self._l2_replacement_policy, "constituency_size"):
                self.l2cache.replacement_policy = self._l2_replacement_policy(
                    constituency_size=self._l2_size
                )
        if self._l2_prefetcher:
            self.l2cache.prefetcher = self._l2_prefetcher()
