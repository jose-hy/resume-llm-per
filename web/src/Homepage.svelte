<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { supabase } from "$lib/supabaseClient";
  import JobForm from "$lib/job_form.svelte";
  import JobListings from "$lib/JobListings.svelte";
  import type { JobListing } from "$lib/types";

  const { sessionID, defaultJobListings, profile } = $props();

  let jobListings: JobListing[] = $state([]);
  let vectorJobs: JobListing[] = $state([]);
  let allVectorJobs: JobListing[] = $state([]);
  let locations: string[] = $state([]);
  let degreeRequirements: string[] = $state([]);
  let employmentType: string[] = $state([]);
  let includeRemoteJobs = $state(false);
  let includeUSCitizenJobsOnly = $state(false);
  let isMoreJobs = $state(true);
  let applied = $state(false);
  let userVector: any = $derived(profile.embedding);
  let userID = $derived(profile.id || "");

  let menu = $state(false);

  const setLocations = (d: string[]) => (locations = d);
  const setDegreeRequirements = (d: string[]) => (degreeRequirements = d);
  const setEmploymentType = (d: string[]) => (employmentType = d);
  const toggleIncludeRemoteJobs = () =>
    (includeRemoteJobs = !includeRemoteJobs);
  const toggleIncludeUSCitizenJobsOnly = () =>
    (includeUSCitizenJobsOnly = !includeUSCitizenJobsOnly);
  

  onMount( async () => {
    // Call jobs based on resume embedding, max 50 with similarity being at least 40%
    try {
      const { data: recs, error } = await supabase.rpc('match_jobs', {
        query_embedding: userVector,
        match_threshold: 0.40,
        match_count: 50,
      });
      if (recs) {
        // Call applied_to and remove any jobs that user already applied to from recs
        const { data, error } = await supabase.from("applied_to").select("*").eq("user_id", userID);
        if (data) {
          const appliedJobIDs = new Set(data.map((job) => job.job_id));
          allVectorJobs = recs.filter((job: JobListing) => !appliedJobIDs.has(job.id));
        } else {
          allVectorJobs = recs as JobListing[];
        }
        vectorJobs = allVectorJobs;
        // Only show 10 jobs and load more with button click
        jobListings = vectorJobs.slice(0, 10) as JobListing[];
        if (vectorJobs.length < 10) {
          isMoreJobs = false;
        }
      }
    } catch (err) {
      console.error(err);
    }
  });

  const getJobListings = async (isNewSearch: boolean) => {
    // Loads more jobs from load more button,
    // Or filters jobListings based on job form
    if (isNewSearch) {
      // Filter jobListings based on filters from job form
      vectorJobs = allVectorJobs.filter((job) => {
        const remoteCheck = includeRemoteJobs ? job.is_remote : true;
        const locationCheck = locations.length > 0 && !locations.includes("All") ? locations.some(loc => job.location.toLowerCase().includes(loc.toLowerCase())) : true;
        return (remoteCheck && locationCheck);
      });
      jobListings = vectorJobs.slice(0, 10);
      if (vectorJobs.length < 10) {
        isMoreJobs = false;
      } else isMoreJobs = true;
    } else {
      // Load more jobs from vector Jobs
      if (vectorJobs.length > 0) {
        const currentLength = jobListings ? jobListings.length : 0;
        const nextJobs = vectorJobs.slice(currentLength, currentLength + 10);
        if (nextJobs.length === 0) {
          isMoreJobs = false;
        } else {
          jobListings = jobListings ? [...jobListings, ...nextJobs] : nextJobs;
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

  onMount(() => {
    window.addEventListener("resize", handleResize);
    handleResize(); // Set initial value

    onDestroy(() => {
      window.removeEventListener("resize", handleResize);
    });
  });
</script>

<svelte:head>
  <title>Interview Moves</title>
</svelte:head>
<div class="flex justify-center pt-48px px-16px">
  <div class="flex gap-24px items-start max-[600px]:flex-col">
    <div class="flex flex-col max-[600px]:gap-2px gap-20px">
      <JobForm
        {getJobListings}
        {setDegreeRequirements}
        {setLocations}
        {setEmploymentType}
        {toggleIncludeRemoteJobs}
        {toggleIncludeUSCitizenJobsOnly}
      />
    </div>
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
