export type JobListing = {
  id: string;
  job_id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  apply_link: string;
  posted_at: string;
  embedding: string;
  similarity?: number;
  is_remote: boolean;
  is_active: boolean;
  expires_at: string;
};

export type OldListing = {
  job_info: string;
  job_post_date: string;
  link: string;
  location_state: string;
  description: string;
  company: string;
  job_location: string;
  job_title: string;
  score: number;
  job_id: string;
  remote: boolean;
};
