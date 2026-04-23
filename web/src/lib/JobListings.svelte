<script lang="ts">
  import JobPreview from "$lib/job_preview.svelte";
  import Spacer from "$lib/spacer.svelte";
  import type { JobListing } from "$lib/types";
  let isLoading = $state(false);

  const {
    sessionID,
    defaultJobListings,
    jobListings,
    getJobListings,
    isMoreJobs,
    applied,
    userID,
  } = $props();

  let appliedHere = $state(applied);
  let jobsClicked = $state(new Set<string>());

  const handleJobClicked = (jobID: string) => {
    if (!jobsClicked.has(jobID)) {
      jobsClicked.add(jobID);
      appliedHere = true;
    }
  };
</script>

<div class="flex flex-col">
  {#if jobListings && jobListings.length > 0}
    {#each jobListings as jobListing}
      <JobPreview
        {jobListing}
        {jobListings}
        {userID}
        {sessionID}
        applied = {appliedHere}
        handleJobClicked={() => handleJobClicked(jobListing.link)}
      />
      <Spacer axis="y" size="16" />
    {/each}
  {:else if jobListings}
    {#if applied}
    <span class="max-w-[650px] w-[45vw] text-center mx-auto">
      <button class="bg-black text-white rounded-4px px-12px py-4px whitespace-nowrap mx-auto mt-16px">
        <a href="/">Explore jobs</a>
      </button>
    </span>
    {:else}
    <p class="max-w-[650px] w-[45vw] text-center">No results found</p>
    {/if}
  {:else}
    {#each defaultJobListings as jobListing}
      <JobPreview
        {jobListing}
        {jobListings}
        {userID}
        {sessionID}
        applied = {appliedHere}
        handleJobClicked={() => handleJobClicked(jobListing.link)}
      />
      <Spacer axis="y" size="16" />
    {/each}
  {/if}
  {#if isMoreJobs}
    <button
      class="bg-black text-white rounded-4px px-12px py-4px
      max-w-min whitespace-nowrap mx-auto flex gap-12px items-center"
      onclick={async () => {
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
