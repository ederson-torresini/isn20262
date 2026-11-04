const { randomUUID } = require("node:crypto");
const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const {
  DynamoDBDocumentClient,
  BatchWriteCommand,
} = require("@aws-sdk/lib-dynamodb");

// DYNAMODB_ENDPOINT só é definido em testes locais (DynamoDB Local).
const client = DynamoDBDocumentClient.from(
  new DynamoDBClient({ endpoint: process.env.DYNAMODB_ENDPOINT || undefined }),
);

const response = (status, body) => ({
  statusCode: status,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

const isNumber = (v) => typeof v === "number" && Number.isFinite(v);

// Valida um banheiro e devolve { item } ou { erro }.
function parse(entry) {
  if (entry === null || typeof entry !== "object" || Array.isArray(entry)) {
    return { erro: "cada banheiro deve ser um objeto JSON" };
  }
  const { latitude, longitude, categorias = [] } = entry;
  if (!isNumber(latitude) || !isNumber(longitude)) {
    return { erro: "latitude e longitude numéricas são obrigatórias" };
  }
  if (Math.abs(latitude) > 90 || Math.abs(longitude) > 180) {
    return { erro: "latitude/longitude fora do intervalo" };
  }
  if (
    !Array.isArray(categorias) ||
    !categorias.every((c) => typeof c === "string" && c.trim() !== "")
  ) {
    return { erro: "categorias deve ser uma lista de strings não vazias" };
  }
  return {
    item: {
      id: randomUUID(),
      latitude,
      longitude,
      categorias: [...new Set(categorias.map((c) => c.trim()))],
    },
  };
}

exports.handler = async (event) => {
  let body = event.body || "";
  if (event.isBase64Encoded) body = Buffer.from(body, "base64").toString();
  let payload;
  try {
    payload = JSON.parse(body);
  } catch {
    return response(400, { erro: "JSON inválido" });
  }

  // Aceita um banheiro ou uma lista deles.
  const entries = Array.isArray(payload) ? payload : [payload];
  if (entries.length === 0) {
    return response(400, { erro: "nenhum banheiro informado" });
  }

  const items = [];
  for (const entry of entries) {
    const { item, erro } = parse(entry);
    if (erro) return response(400, { erro });
    items.push(item);
  }

  // BatchWrite aceita no máximo 25 itens por chamada.
  for (let i = 0; i < items.length; i += 25) {
    let requests = items
      .slice(i, i + 25)
      .map((Item) => ({ PutRequest: { Item } }));
    while (requests.length) {
      const out = await client.send(
        new BatchWriteCommand({
          RequestItems: { [process.env.TABLE_NAME]: requests },
        }),
      );
      requests = out.UnprocessedItems?.[process.env.TABLE_NAME] || [];
    }
  }

  return response(201, { ids: items.map((i) => i.id) });
};
