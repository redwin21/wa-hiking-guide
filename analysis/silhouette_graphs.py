import matplotlib
import numpy as np
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples

def silhouette_graphs(X, n_clusters):
    sil_scores = []
    # taken from sklearn
    fig, axs = plt.subplots(len(n_clusters), 1, figsize=(10,10))

    for idx, ax in enumerate(axs.flatten()):

        # The 1st subplot is the silhouette plot
        # The silhouette coefficient can range from -1, 1 but in this example all
        # lie within [-0.1, 1]
        ax.set_xlim([-0.3, 1])
        # The (n_clusters+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        ax.set_ylim([0, X.shape[0] + (n_clusters[idx] + 1) * 10])

        # Initialize the clusterer with n_clusters value and a random generator
        # seed of 10 for reproducibility.
        clusterer = KMeans(n_clusters=n_clusters[idx], random_state=10)
        cluster_labels = clusterer.fit_predict(X)

        # The silhouette_score gives the average value for all the samples.
        # This gives a perspective into the density and separation of the formed
        # clusters
        silhouette_avg = silhouette_score(X, cluster_labels)
        sil_scores.append(silhouette_avg)

        # The vertical line for average silhoutte score of all the values
        ax.axvline(x=silhouette_avg, color="red", linestyle="--")

        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(X, cluster_labels)

        y_lower = 10
        for i in range(n_clusters[idx]):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = \
                sample_silhouette_values[cluster_labels == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = matplotlib.cm.nipy_spectral(float(i) / n_clusters[idx])
            ax.fill_betweenx(np.arange(y_lower, y_upper),
                            0, ith_cluster_silhouette_values,
                            facecolor=color, edgecolor=color, alpha=0.7)

            # Label the silhouette plots with their cluster numbers at the middle
            ax.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        ax.set_xlabel("Silhouette Coefficient Values")
        ax.set_ylabel("Cluster label")

        ax.set_yticks([])  # Clear the yaxis labels / ticks
        ax.set_xticks([-0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])


        # Labeling the clusters
        ax.legend(['Average silhouette = %.2f' % silhouette_avg], loc='lower right', framealpha=1)

        plt.suptitle(("Silhouette Analysis for KMeans Clustering "),
                    fontsize=14, fontweight='bold')

    return fig, sil_scores