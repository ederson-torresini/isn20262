const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const {
  DynamoDBDocumentClient,
  ScanCommand,
} = require("@aws-sdk/lib-dynamodb");

// DYNAMODB_ENDPOINT só é definido em testes locais (DynamoDB Local).
const client = DynamoDBDocumentClient.from(
  new DynamoDBClient({ endpoint: process.env.DYNAMODB_ENDPOINT || undefined }),
);

async function scanAll() {
  const items = [];
  let startKey;
  do {
    const page = await client.send(
      new ScanCommand({
        TableName: process.env.TABLE_NAME,
        ExclusiveStartKey: startKey,
      }),
    );
    items.push(...page.Items);
    startKey = page.LastEvaluatedKey;
  } while (startKey);
  return items;
}

exports.handler = async () => ({
  statusCode: 200,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(await scanAll()),
});
