<script lang="ts">
  import JobListings from "./JobListings.svelte";
  import type { JobListing } from "$lib/types";
  import { onMount, onDestroy } from "svelte";
  import { backendURL, get, post } from "../utils";

  const { sessionID, defaultJobListings } = $props();

  let jobListings: JobListing[] | null = $state(null);
  let includeRemoteJobs = $state(false);
  let includeUSCitizenJobsOnly = $state(false);
  let locations: string[] = $state([]);
  let degreeRequirements: string[] = $state([]);
  let employmentType: string[] = $state([]);
  let file: Blob | string = $state("");
  let isMoreJobs = $state(true);
  let applied = $state(true);

  let menu = $state(false);


  const getJobListings = async (isNewSearch: boolean) => {
    try {
      const url = new URL(backendURL("/search_jobs"));
      for (let i = 0; i < locations.length; i++) {
        url.searchParams.append("location_state", locations[i]);
      }
      for (let i = 0; i < degreeRequirements.length; i++) {
        url.searchParams.append(
          "degree",
          degreeRequirements[i].split(" ").join("_").toLowerCase(),
        );
      }
      for (let i = 0; i < employmentType.length; i++) {
        url.searchParams.append("employment_type", employmentType[i]);
      }
      const formData = new FormData();
      formData.append("file", file);
      formData.append("rerank", "true");
      formData.append("result_count", "10");
      formData.append("offset", String(jobListings?.length ?? 0));
      formData.append("limit", "10");
      formData.append("remote", String(includeRemoteJobs));
      formData.append(
        "exclude_citizen_only",
        String(!includeUSCitizenJobsOnly),
      );

      const res = await fetch(url, {
        headers: {
          Accept: "application/json",
        },
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (isNewSearch) {
        if (
          data?.message ===
          "No matching jobs found for your resume and filters."
        ) {
          jobListings = [];
        } else {
          jobListings = data;
          if (data.length < 10) {
            isMoreJobs = false;
          }
        }
      } else if (jobListings) {
        jobListings = [...jobListings, ...data];
        if (data.length < 10) {
          isMoreJobs = false;
        }
      }
    } catch (err) {
      console.log(err);
    }
  };

  onMount(async () => {
    await Promise.all([
      post("/analytics/initializeAnalytics", {
        type: "jobs_viewed",
        data: JSON.stringify({
          session_id: sessionID,
          clicked_on: 0,
          viewed: 10,
        }),
      }),
      post("/analytics/initializeAnalytics", {
        type: "dau", // Daily Active Users
        data: JSON.stringify({ count: 1, session_id: sessionID }),
      }),
    ]);
  });

  function handleResize() {
    if (window.innerWidth < 600) {
      menu = false;
    } else {
      menu = true;
    }
  }

  onMount(() => {
    window.addEventListener("resize", handleResize);
    handleResize(); // Set initial value

    onDestroy(() => {
      window.removeEventListener("resize", handleResize);
    });
  });
</script>

<div class="w-2/3">
  <h1 class="font-600 text-24px">Applied Jobs:</h1>
  <div>
    <JobListings
      {getJobListings}
      {jobListings}
      {sessionID}
      {defaultJobListings}
      {file}
      {isMoreJobs}
      {applied}
    />
  </div>
</div>