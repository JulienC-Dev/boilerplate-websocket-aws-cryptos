# WebSocket Server and Clients Deployment

This project facilitates the deployment of a WebSocket server using AWS API Gateway and Terraform, along with the generation of multiple WebSocket clients that connect to various data sources, such as blockchain networks (e.g., Arbitrum, Ethereum) and centralized exchanges (e.g., Binance). Each WebSocket client is containerized and managed through Docker.

For a detailed explanation of the architecture and step-by-step instructions, please visit the blog post on my website: [https://julienc.vercel.app/blog/websokets-python-terraform-aws-services](https://julienc.vercel.app/blog/websokets-python-terraform-aws-services).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Deploying the WebSocket Server](#deploying-the-websocket-server)
4. [Creating WebSocket Clients](#creating-websocket-clients)
   - [For Decentralized Finance (DeFi) Networks](#for-decentralized-finance-defi-networks)
   - [For Centralized Exchanges](#for-centralized-exchanges)
5. [Automating Deployment with GitHub Actions](#automating-deployment-with-github-actions)
6. [Contributing](#contributing)
7. [License](#license)

## Prerequisites

Ensure you have the following tools installed before getting started:

- **Docker**: For container management.
- **Terraform**: For infrastructure as code.
- **AWS CLI**: To deploy the WebSocket server on AWS.
- **Python**: Required for running the client scripts.
- **Node Provider**: To get data from the blockchain networks. You need one node provider for each network you want to connect to.

## Project Structure

```plaintext
.
├── /websocket_server/
│   └── terraform/            # Contains Terraform configurations to deploy the WebSocket client
├── /websocket_clients/
│   ├── Dockerfile            # Shared Dockerfile for both DeFi and exchange clients
│   ├── /scripts/             # Contains scripts for different data sources
│   │   ├── defi/             # Scripts for DeFi networks (e.g., Arbitrum, Ethereum)
│   │   └── exchange/         # Scripts for centralized exchanges (e.g., Binance)
├── .github/                  # GitHub Actions workflows for CI/CD
└── README.md                 # This README file
```

## Deploying the WebSocket Server

The WebSocket server is deployed using Terraform with AWS API Gateway as the deployment target. Follow the instructions in the `/websocket_server/terraform/` directory to set up and deploy the server.

### Steps:

1. **Navigate to the Terraform directory**:

   ```bash
   cd websocket_server/terraform/
   ```

2. **Initialize Terraform**:

   ```bash
   terraform init
   ```

3. **Apply the Terraform plan**:
   ```bash
   terraform apply
   ```
   Confirm the changes to deploy the WebSocket server.

## Creating WebSocket Clients

### For Decentralized Finance (DeFi) Networks

Each WebSocket client is designed to connect to a specific blockchain network (e.g., Arbitrum, Ethereum). To create and launch a client, follow these steps:

1. **Navigate to the desired client directory**:

   ```bash
   cd websocket_clients/networks_arbitrum/
   docker build -t networks_arbitrum .
   ```

2. **Run the Docker container**:
   The following command will add the Arbitrum network to the Brownie configuration and run the WebSocket client script for the Arbitrum network.

   ```bash
   docker run -d networks_arbitrum /bin/bash -c "
       brownie networks add Arbitrum arbitrum-mainnet host=https://arb-mainnet.g.alchemy.com/v2/\$WEB3_ALCHEMY_PROJECT_ID_ARBITRUM_MAINNET chainid=42161 &&
       brownie run /usr/src/app/scripts/defi/websocket_client_defi.py --network=arbitrum-mainnet
   "
   ```

3. **Add more Pools and Networks to brownie-config as needed**:
   you can follow the structure of the `brownie-config.yaml` file to add more pools and networks to the configuration.

### For Centralized Exchanges

1. **Navigate to the desired client directory**:

   ```bash
   cd websocket_clients/exchange_binance/
   docker build -t exchange_binance .
   ```

2. **Run the Docker container**:
   The following command will run the WebSocket client script for the Binance exchange.
   ```bash
   docker run -d exchange_binance /bin/bash -c "
       python /usr/src/app/scripts/exchange/websocket_client_exchange.py -e binance
   "
   ```

## Automating Deployment with GitHub Actions

You can automate your deployment process using GitHub Actions. This includes running AWS-related tasks, such as deploying to ECS, through CI/CD pipelines defined in your repository's `.github/` directory.

To get started, ensure your GitHub Actions workflows are properly set up in the `.github/workflows/` directory. These workflows can handle tasks like:

- Automatically deploying changes to the WebSocket server.
- Building and pushing Docker images for WebSocket clients.
- Running tests and checks on your infrastructure code.

## Contributing

Contributions are welcome! If you have suggestions for improvements, feel free to open an issue or submit a pull request.

Please follow the [Contributor Guidelines](CONTRIBUTING.md) to ensure a smooth contribution process.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
