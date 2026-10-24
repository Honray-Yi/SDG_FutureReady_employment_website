export * from "./generated/api";
export * from "./generated/types";
// Orval emits a query schema and a query type with the same name.
// Select the schema explicitly; expose the structural type under a distinct name.
export { GetJobCoursesParams } from "./generated/api";
export type { GetJobCoursesParams as JobCoursesQuery } from "./generated/types/getJobCoursesParams";
