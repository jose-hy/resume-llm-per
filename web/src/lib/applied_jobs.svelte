<script lang="ts">
  import type { JobListing } from "$lib/types";
  import { onMount, onDestroy } from "svelte";
  import Spacer from "./spacer.svelte";
  import { supabase } from "$lib/supabaseClient.js";
  import JobListings from "$lib/JobListings.svelte";

  const { sessionID, userID, defaultJobListings } = $props();

  let jobListings: JobListing[] = $state([]);
  let allJobs: JobListing[] = $state([]);
  //let includeRemoteJobs = $state(false);
  //let includeUSCitizenJobsOnly = $state(false);
  //let locations: string[] = $state([]);
  //let degreeRequirements: string[] = $state([]);
  //let employmentType: string[] = $state([]);
  //let file: Blob | string = $state("");
  let isMoreJobs = $state(true);
  let applied = $state(true);
  let menu = $state(false);

  onMount(async () => {
    window.addEventListener("resize", handleResize);
    handleResize(); // Set initial value

    onDestroy(() => {
      window.removeEventListener("resize", handleResize);
    });

    try {
      const { data, error } = await supabase.from("applied_to").select("*").eq("user_id", userID);
      if (data) {
        allJobs = data as JobListing[];
        jobListings = data.slice(0, 10) as JobListing[];
        if (data.length < 10) {
          isMoreJobs = false;
        }
      }
    } catch (err) {
      console.log(err);
    }

  });

  const getJobListings = async (isNewSearch: boolean) => {
    if (isNewSearch) {
      // This JobListings will never do a new search
    } else {
      if (allJobs.length > 0) {
        const currentLength = jobListings.length;
        const nextJobs = allJobs.slice(currentLength, currentLength + 10);
        if (nextJobs.length === 0) {
          isMoreJobs = false; 
        } else {
          jobListings = [...jobListings, ...nextJobs];
        }
      } else {
        isMoreJobs = false;
      }
    }
  };

  function handleResize() {
    if (window.innerWidth < 600) {
      menu = false;
    } else {
      menu = true;
    }
  }
</script>

<div class="w-2/3">
  <h1 class="font-600 text-24px">Applied Jobs:</h1>
  <div>
    <JobListings
      {getJobListings}
      {jobListings}
      {sessionID}
      {userID}
      {defaultJobListings}
      {isMoreJobs}
      {applied}
    />
  </div>
</div>