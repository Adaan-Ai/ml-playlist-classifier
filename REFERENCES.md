# References and data notes

1. Awadelkarim, A. and Coelho, K. (2018). “Training a Playlist Curator Based on User Taste.” CS229 project report. https://cs229.stanford.edu/proj2018/report/22.pdf
2. Awadelkarim, A. and Coelho, K. (2018). “Training a Playlist Curator Based on User Taste.” CS229 project poster. https://cs229.stanford.edu/proj2018/poster/22.pdf
3. TidyTuesday, 2020-01-21 Spotify Songs dataset. Data dictionary and provenance included in the user's archive; the README says the data was collected from Spotify using the `spotifyr` package. Dataset landing page: https://github.com/rfordatascience/tidytuesday/tree/master/data/2020/2020-01-21
4. Spotify for Developers. “Spotify Developer Policy,” effective 15 May 2025. https://developer.spotify.com/policy
5. Spotify for Developers (27 November 2024). “Introducing some changes to our Web API.” https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api
6. Defferrard, M., Benzi, K., Vandergheynst, P., and Bresson, X. (2017). “FMA: A Dataset For Music Analysis.” ISMIR. https://arxiv.org/abs/1612.01840
7. FMA dataset code and metadata description. https://github.com/mdeff/fma

## Data provenance and use

The supplied ZIP contains a README with a Spotify Songs data dictionary and provenance note. The README does not state a redistribution license. Do not commit or redistribute the raw CSV without checking its terms. Spotify's current Developer Policy prohibits using Spotify content to train ML models. Because the assignment is academic and the instructor may authorize an archival dataset for this work, confirm that use with the course staff. The code does not access the Spotify API. If the instructor does not approve the supplied data, FMA is an open alternative with track features and genre metadata; see Defferrard et al. and the FMA repository.
