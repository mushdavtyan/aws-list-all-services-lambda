// The default behavior is to inventory only the account the lambda function
// is installed in (i.e. accounts_info = "self"
module "example_self" {
  source_file  = "../release/inventory-lambda.zip"
  appenv       = "staging"
  project_name = "allcloud"
}
