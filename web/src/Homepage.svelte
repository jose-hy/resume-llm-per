<script lang="ts">
  import { onMount } from "svelte";
  import JobForm from "$lib/job_form.svelte";
  import { get, post } from "./utils";
  import { invalidateAll } from "$app/navigation";
  import JobListings from "$lib/JobListings.svelte";
  import type { JobListing } from "$lib/types";

  const { sessionID, defaultJobListings } = $props();

  let jobListings: JobListing[] | null = $state(null);
  let includeRemoteJobs = $state(false);
  let includeUSCitizenJobsOnly = $state(false);
  let locations: string[] = $state([]);
  let degreeRequirements: string[] = $state([]);
  let employmentType: string[] = $state([]);
  let file: Blob | string = $state("");
  let isMoreJobs = $state(true);

  const setDegreeRequirements = (d: string[]) => (degreeRequirements = d);
  const setLocations = (d: string[]) => (locations = d);
  const setEmploymentType = (d: string[]) => (employmentType = d);
  const setFile = (d: Blob | string) => (file = d);
  const toggleIncludeUSCitizenJobsOnly = () =>
    (includeUSCitizenJobsOnly = !includeUSCitizenJobsOnly);
  const toggleIncludeRemoteJobs = () =>
    (includeRemoteJobs = !includeRemoteJobs);

  const getJobListings = async (isNewSearch: boolean) => {
    try {
      const url = new URL(
        "https://jobmatch-api.orangemoss-fa3f1656.eastus.azurecontainerapps.io/api/v1/search_jobs",
      );
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
        type: "dau",
        data: JSON.stringify({ count: 1, session_id: sessionID }),
      }),
    ]);
  });

  const logout = async () => {
    await get("/logout_user");
    invalidateAll();
  };
</script>

<svelte:head>
  <title>Interview Moves</title>
</svelte:head>
<div class="flex justify-center pt-48px px-16px">
  <div class="flex gap-24px items-start max-[600px]:flex-col">
    <!-- <button onclick={logout}>logout</button> -->
    <JobForm
      {getJobListings}
      {setDegreeRequirements}
      {setLocations}
      {setEmploymentType}
      {setFile}
      {toggleIncludeRemoteJobs}
      {toggleIncludeUSCitizenJobsOnly}
    />
    <JobListings
      {getJobListings}
      {jobListings}
      {sessionID}
      {defaultJobListings}
      {file}
      {isMoreJobs}
    />
  </div>
</div>
