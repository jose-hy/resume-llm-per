<script lang="ts">
  import JobPreview from "$lib/job_preview.svelte";
  import Spacer from "$lib/spacer.svelte";
  import { put } from "../utils";

  let isLoading = $state(false);

  const {
    sessionID,
    defaultJobListings,
    jobListings,
    getJobListings,
    file,
    isMoreJobs,
  } = $props();

  let jobsClicked = $state(new Set<string>());

  const updateJobsViewed = async (
    jobsCountIncrease: number,
    jobsViewedIncrease: number,
  ) => {
    await put("/analytics/updateJobsViewed", {
      jobs_count: jobsCountIncrease,
      jobs_viewed: jobsViewedIncrease,
      session_id: sessionID,
    });
  };

  const handleJobClicked = (jobID: string) => {
    if (!jobsClicked.has(jobID)) {
      jobsClicked.add(jobID);
      updateJobsViewed(0, 1);
    }
  };
</script>

<div class="flex flex-col">
  {#if jobListings && jobListings.length > 0}
    {#each jobListings as jobListing}
      <JobPreview
        {jobListing}
        {jobListings}
        {file}
        handleJobClicked={() => handleJobClicked(jobListing.link)}
      />
      <Spacer axis="y" size="16" />
    {/each}
  {:else if jobListings}
    <p class="max-w-[650px] w-[45vw] text-center">No results found</p>
  {:else}
    {#each defaultJobListings as jobListing}
      <JobPreview
        {jobListing}
        {jobListings}
        {file}
        handleJobClicked={() => handleJobClicked(jobListing.link)}
      />
      <Spacer axis="y" size="16" />
    {/each}
  {/if}
  {#if jobListings && jobListings.length > 0 && isMoreJobs}
    <button
      class="bg-black text-white rounded-4px px-12px py-4px
      max-w-min whitespace-nowrap mx-auto flex gap-12px items-center"
      onclick={async () => {
        updateJobsViewed(10, 0);

        isLoading = true;
        await getJobListings(false);
        isLoading = false;
      }}
      disabled={isLoading}
    >
      {#if isLoading}
        Loading
        <div
          class="border-t-[white] border-l-[white] border-b-[white]
          w-[16px] h-[16px] border-[2px] border-transparent
          spinner animate-spin rounded-circle"
        ></div>
      {:else}
        Load more
      {/if}
    </button>
  {/if}
  <Spacer axis="y" size="48" />
</div>
