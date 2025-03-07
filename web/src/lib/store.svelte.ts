export type JobListing = {
  job_info: string;
  job_post_date: string;
  link: string;
  location_state: string;
  description: string;
  company: string;
  job_location: string;
  job_title: string;
  score: number;
};

function createStore() {
  let jobListings: JobListing[] | null = $state(null);
  let defaultJobListings: JobListing[] = $state([]);
  let includeRemoteJobs = $state(false);
  let includeUSCitizenJobsOnly = $state(false);
  let locations: string[] = $state([]);
  let degreeRequirements: string[] = $state([]);
  let employmentType: string[] = $state([]);
  let file: Blob | string = $state("");

  return {
    get defaultJobListings() {
      return defaultJobListings;
    },
    get jobListings() {
      return jobListings;
    },
    get file() {
      return file;
    },
    get includeRemoteJobs() {
      return includeRemoteJobs;
    },
    get locations() {
      return locations;
    },
    get includeUSCitizenJobsOnly() {
      return includeUSCitizenJobsOnly;
    },
    setEmploymentType: (newEmploymentType: string[]) =>
      (employmentType = newEmploymentType),
    setLocations: (newLocations: string[]) => (locations = newLocations),
    setDegreeRequirements: (newDegreeRequirements: string[]) =>
      (degreeRequirements = newDegreeRequirements),
    setFile: (newFile: Blob | string) => (file = newFile),
    toggleIncludeRemoteJobs: () => (includeRemoteJobs = !includeRemoteJobs),
    toggleIncludeUSCitizenJobsOnly: () =>
      (includeUSCitizenJobsOnly = !includeUSCitizenJobsOnly),
    getDefaultJobListings: async () => {},
    getJobListings: async (isNewSearch: boolean) => {
      try {
        const url = new URL(
          "https://jobmatch-api.orangemoss-fa3f1656.eastus.azurecontainerapps.io/api/v1/search_jobs"
        );
        for (let i = 0; i < locations.length; i++) {
          url.searchParams.append("location_state", locations[i]);
        }
        for (let i = 0; i < degreeRequirements.length; i++) {
          url.searchParams.append(
            "degree",
            degreeRequirements[i].split(" ").join("_").toLowerCase()
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
          String(!includeUSCitizenJobsOnly)
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
          }
        } else if (jobListings) {
          jobListings = [...jobListings, ...data];
        }
      } catch (err) {
        console.log(err);
      }
    },
  };
}

export const store = createStore();
