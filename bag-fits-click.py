import click

@click.command()
def hello():
    click.echo('yay')

if __name__ == '__main__':
    hello()
