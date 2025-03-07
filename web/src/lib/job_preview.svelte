<script lang="ts">
  import Spacer from "./spacer.svelte";
  import Dialog from "$lib/dialog.svelte";
  import dayjs from "dayjs";
  import relativeTime from "dayjs/plugin/relativeTime";
  import { store, type JobListing } from "./store.svelte";
  import { stateAbbreviations } from "../utils";

  dayjs.extend(relativeTime);

  const {
    handleJobClicked,
    jobListing,
  }: {
    handleJobClicked: () => void;
    jobListing: JobListing;
  } = $props();

  //   {
  //     "job_id": "YeoKwsBFAl3BvPNiAAAAAA==",
  //     "job_title": "2025 Software Dev Engineer Intern - Embedded, Runtime, Storage, System & Performance, Annapurna Labs",
  //     "job_location": "Cupertino, California",
  //     "company": "Amazon Web Services (AWS)",
  //     "description": "Description\n\nAmazon Web Services (AWS) internships are full-time (40 hours/week) for 12 consecutive weeks. By applying to this position, your application will be considered for all locations we hire for in the United States.\n\nAre you excited about Machine Learning, chip acceleration, compilers, storage, systems or EC2? Are you passionate about delivering high quality services that affect hundreds of thousands of users? We are the dubbed the \"secret sauce\" behind AWS's success with development centers in the U.S. and Israel, and Amazon is at the forefront of innovation by combining cloud scale with the world’s most talented engineers.\n\nIf this sounds exciting to you - come build the future with us!\n\nKey job responsibilities\n\nInnovating and delivering creative SW Designs to develop new services, solve operational problems, drive improvements in developer velocity, or positively impact operational safety\n\nWriting requirements capturing documents, design documents, integration test plans, and deployment plans\n\nCommunicating status and progress of deliverables to schedule, and sharing learnings/ innovations with your team and stakeholders\n\nBasic Qualifications\n• Currently enrolled in a Bachelor’s degree program or higher majoring in Computer Science, Computer Engineering, Electrical Engineering or related technical field with anticipated graduation date of December 2025 or later\n• Programming experience in internship or coursework with programming language such as Python and/or C or C++\n• Candidates with strong interests and academic qualifications/research focus in two of the following: 1. Distributed systems, algorithms (MPI, NCCL, or similar), 2. Operating Systems, 3. Linux system programming/services, 4. Computer architecture, 5. System Development, 6. Complexity analysis\n\nPreferred Qualifications\n• Previous technical internship(s), if applicable.\n• Experience with distributed, multi-tiered systems, algorithms, and relational databases.\n• Experience in optimization mathematics such as linear programming and nonlinear optimization\n• Adept at handling ambiguous or undefined problems as well as ability to think abstractly.\n\nAmazon is committed to a diverse and inclusive workplace. Amazon is an equal opportunity employer and does not discriminate on the basis of race, national origin, gender, gender identity, sexual orientation, protected veteran status, disability, age, or other legally protected status.\n\nLos Angeles County applicants: Job duties for this position include: work safely and cooperatively with other employees, supervisors, and staff; adhere to standards of excellence despite stressful conditions; communicate effectively and respectfully with employees, supervisors, and staff to ensure exceptional customer service; and follow all federal, state, and local laws and Company policies. Criminal history may have a direct, adverse, and negative relationship with some of the material job duties of this position. These include the duties and responsibilities listed above, as well as the abilities to adhere to company policies, exercise sound judgment, effectively manage stress and work safely and respectfully with others, exhibit trustworthiness and professionalism, and safeguard business operations and the Company’s reputation. Pursuant to the Los Angeles County Fair Chance Ordinance, we will consider for employment qualified applicants with arrest and conviction records.\n\nOur inclusive culture empowers Amazonians to deliver the best results for our customers. If you have a disability and need a workplace accommodation or adjustment during the application and hiring process, including support for the interview or onboarding process, please visit https://amazon.jobs/content/en/how-we-hire/accommodations for more information. If the country/region you’re applying in isn’t listed, please contact your Recruiting Partner.\n\nOur compensation reflects the cost of labor across several US geographic markets. The base pay for this position ranges from $47.84/hr in our lowest geographic market up to $96.15/hr in our highest geographic market. Pay is based on a number of factors including market location and may vary depending on job-related knowledge, skills, and experience. Amazon is a total compensation company. Dependent on the position offered, equity, sign-on payments, and other forms of compensation may be provided as part of a total compensation package, in addition to a full range of medical, financial, and/or other benefits. For more information, please visit https://www.aboutamazon.com/workplace/employee-benefits. This position will remain posted until filled. Applicants should apply via our internal or external career site.\n\nCompany - Amazon Data Services, Inc.\n\nJob ID: A2794071",
  //     "score": 0.9079672,
  //     "degree": "required",
  //     "remote": false,
  //     "location_state": "California",
  //     "employment_type": "Full-time",
  //     "citizen": true,
  //     "link": "https://www.linkedin.com/jobs/view/2025-software-dev-engineer-intern-embedded-runtime-storage-system-performance-annapurna-labs-at-amazon-web-services-aws-4040163687?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic",
  //     "job_post_date": "2025-02-16T00:00:00.000Z"
  // }

  const generateScoreString = (score: number) => {
    let str = "";

    if (score <= 0.2) {
      str = "Minimal Match";
    } else if (score <= 0.4) {
      str = "Low Match";
    } else if (score <= 0.6) {
      str = "Moderate Match";
    } else if (score <= 0.8) {
      str = "Good Match";
    } else {
      str = "Strong Match";
    }

    return `${str} (${(score * 100).toFixed(0).toString()}%)`;
  };

  const {
    job_post_date,
    link,
    description,
    company,
    job_location,
    job_title,
    score,
  } = jobListing;

  const [city, state] = job_location.split(",").map((s) => s.trim());
  const abbrState = { ...stateAbbreviations, "District of Columbia": "DC" }[
    state
  ];

  let descriptionPreview = description.slice(0, 200);

  const formattedTime = dayjs(job_post_date).fromNow();

  const scoreString = generateScoreString(score);
</script>

<div
  class="bg-white [border:1px_solid_#DADADA] rounded-8px max-w-[650px] px-20px py-14px"
>
  <div class="flex justify-between gap-[20px]">
    <div>
      <p class="font-700 text-18px">{job_title}</p>
      <p class="14px font-500">
        {company}
      </p>
      <p class="14px">
        {city}, {abbrState} | {formattedTime}
      </p>
    </div>
    {#if store.jobListings}
      <p
        class={"bg-[#ECE5AC] max-w-min whitespace-nowrap h-full px-[6px] py-4px rounded-4px text-14px"}
      >
        {scoreString}
      </p>
    {/if}
  </div>
  <Spacer axis="y" size="12" />
  <p class="text-[#383838]">
    {descriptionPreview + (descriptionPreview.at(-1) === "." ? "" : "...")}
  </p>
  <Spacer axis="y" size="24" />
  <div class="flex items-baseline gap-8px">
    <div>
      <a
        class="bg-black text-white rounded-4px px-12px py-4px h-full"
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        onclick={handleJobClicked}
      >
        Apply
      </a>
    </div>
    <Dialog
      {description}
      {company}
      {job_title}
      {city}
      {abbrState}
      {link}
      {formattedTime}
    />
  </div>
</div>
