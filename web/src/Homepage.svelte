<script lang="ts">
  import { onMount } from "svelte";
  import JobForm from "$lib/job_form.svelte";
  import JobPreview from "$lib/job_preview.svelte";
  import Spacer from "$lib/spacer.svelte";
  import { get, post, put } from "./utils";
  import { invalidateAll } from "$app/navigation";

  import { store } from "./lib/store.svelte";
  let isLoading = $state(false);

  const data = $props();

  let isAtLeastOneJobSelected = $state(false);
  let jobsClicked = $state(new Set<string>());

  const initializeAtLeastOneJobSelected = async () => {
    await post("/analytics/atLeastOneJobSelected", {
      type: "at_least_one_job_selected",
      data: JSON.stringify({ value: false, session_id: data.sessionID }),
    });
  };

  onMount(async () => {
    await Promise.all([
      store.getDefaultJobListings(),
      initializeAtLeastOneJobSelected(),
      post("/analytics/initializeAnalytics", {
        type: "jobs_viewed",
        data: JSON.stringify({
          session_id: data.sessionID,
          clicked_on: 0,
          viewed: 10,
        }),
      }),
      post("/analytics/initializeAnalytics", {
        type: "dau",
        data: JSON.stringify({ count: 1, session_id: data.sessionID }),
      }),
    ]);
  });

  const updateJobsViewed = async (
    jobsCountIncrease: number,
    jobsViewedIncrease: number
  ) => {
    await put("/analytics/updateJobsViewed", {
      jobs_count: jobsCountIncrease,
      jobs_viewed: jobsViewedIncrease,
      session_id: data.sessionID,
    });
  };

  const handleJobClicked = (jobID: string) => {
    if (!isAtLeastOneJobSelected) {
      initializeAtLeastOneJobSelected();
      isAtLeastOneJobSelected = true;
    }

    if (!jobsClicked.has(jobID)) {
      jobsClicked.add(jobID);
      updateJobsViewed(0, 1);
    }
  };

  const logout = async () => {
    await get("/logout_user");
    invalidateAll();
  };
</script>

<div class="flex justify-center pt-48px px-16px">
  <div class="flex gap-24px items-start max-[600px]:flex-col">
    <button onclick={logout}>logout</button>
    <JobForm />
    <div class="flex flex-col">
      {#if store.jobListings && store.jobListings.length > 0}
        {#each store.jobListings as jobListing}
          <JobPreview
            {jobListing}
            handleJobClicked={() => handleJobClicked(jobListing.link)}
          />
          <Spacer axis="y" size="16" />
        {/each}
      {:else if store.jobListings}
        <p class="max-w-[650px] w-[45vw] text-center">No results found</p>
      {:else}
        {#each data.defaultJobListings as jobListing}
          <JobPreview
            {jobListing}
            handleJobClicked={() => handleJobClicked(jobListing.link)}
          />
          <Spacer axis="y" size="16" />
        {/each}
      {/if}
      {#if store.jobListings && store.jobListings.length > 0}
        <button
          class="bg-black text-white rounded-4px px-12px py-4px max-w-min whitespace-nowrap mx-auto flex gap-12px items-center"
          onclick={async () => {
            updateJobsViewed(10, 0);

            isLoading = true;
            await store.getJobListings(false);
            isLoading = false;
          }}
          disabled={isLoading}
          >{#if isLoading}
            Loading
            <div
              class="border-t-[white] border-l-[white] border-b-[white]
        w-[16px] h-[16px] border-[2px] border-transparent spinner animate-spin rounded-circle"
            ></div>
          {:else}
            Load more
          {/if}</button
        >
      {/if}
      <Spacer axis="y" size="48" />
    </div>
  </div>
</div>
