# Deploying the Agentic Website to Fly.io

This README provides a quick overview of the deployment process for the agentic website to Fly.io.

## Quick Start

1. Clone this repository
2. Install the Fly CLI: `curl -L https://fly.io/install.sh | sh`
3. Login to Fly.io: `fly auth login`
4. Deploy the application: `fly launch`
5. Set environment variables: `fly secrets set KEY=VALUE`
6. Open your application: `fly open`

## Documentation

For detailed instructions, refer to these documents:

- [FLY_DEPLOYMENT_GUIDE.md](./FLY_DEPLOYMENT_GUIDE.md) - Comprehensive step-by-step guide
- [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) - Overview of the deployment setup

## Files

The deployment setup includes:

- `Dockerfile` - Defines how to containerize the application
- `.dockerignore` - Excludes unnecessary files from the Docker image
- `fly.toml.example` - Example configuration for Fly.io (will be generated during `fly launch`)
- `health_check.py` - Health check endpoint for monitoring
- `.github/workflows/fly.yml` - GitHub Actions workflow for CI/CD

## CI/CD Setup (Optional)

To set up CI/CD with GitHub Actions:

1. Generate a Fly API token: `fly auth token`
2. Add the token as a GitHub secret named `FLY_API_TOKEN`
3. Push code to your main branch to trigger automatic deployment

## Troubleshooting

If you encounter issues:

1. Check application status: `fly status`
2. View logs: `fly logs`
3. Verify your environment variables: `fly secrets list`
4. Ensure your application is healthy: Visit `/health` endpoint

## Questions?

Refer to the [FLY_DEPLOYMENT_GUIDE.md](./FLY_DEPLOYMENT_GUIDE.md) for detailed information, or check the [Fly.io documentation](https://fly.io/docs/). 