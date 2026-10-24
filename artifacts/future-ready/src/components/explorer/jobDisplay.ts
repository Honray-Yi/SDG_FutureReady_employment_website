import type { Job } from '@workspace/api-client-react';
import type { Language } from '../../i18n';
export const jobName = (job: Job, language: Language) => language === 'en' ? job.job_name_en ?? 'Role translation unavailable' : job.job_name;
export const jobText = (job: Job, language: Language) => language === 'en' ? job.job_text_en ?? 'English summary unavailable.' : job.job_text;
